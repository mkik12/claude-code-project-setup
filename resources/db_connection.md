# Connection to the Application Database

## Purpose

This document describes the connection to an application's own database. This document is a
generic specification. Use it to build a skill for Claude or GitHub Copilot.

## Connection Principle

The application owns a PostgreSQL database. A platform connector provisions this database. The
application uses a connection pool. The pool has a small minimum size and a small maximum size.

The application creates the pool at startup, inside the app factory. The application never opens a
database connection at import time. An early import-time connection could crash-loop the process
before the health-check endpoint exists.

The database is optional. The application must start without it. The application must serve every
read-only path without it. A missing or broken connection disables persistence only. It never stops
the application.

The application runs schema migrations right after the pool opens. Migrations run under one
database advisory lock. The lock stops two replicas from migrating at the same time. Each migration
carries a checksum. A changed checksum on an already-applied migration aborts startup migrations
and disables persistence. A failed migration never crashes the process. Each migration is applied
once, in order, and never edited after it ships.

The database may store two kinds of data. Pick one rule per kind of data; do not mix them.

1. **Owned records.** Records that only the database holds, for example saved documents or saved
   snapshots. Each record follows a lifecycle, for example `draft` → `published` → `archived`. Each
   update uses an optimistic revision check. Deletes are often disallowed; archiving replaces them.
2. **Mirrored working state.** Data that also lives in an in-memory runtime store. The in-memory
   store is the source of truth for this data. The database only mirrors it. The application writes
   to the mirror after every mutation. The application never blocks a request on that write.

When the application mirrors working state, it namespaces the mirror by a mode or tenant key. Each
mode owns its own rows. The application hydrates the mirror over the in-memory defaults at startup.
The application validates every hydrated row. A row that fails validation is quarantined. A
quarantined row never reaches the runtime store or any downstream computation. A quarantined row
stays in the mirror for an administrator to inspect.

## Required Environment Variables

The application reads variables for the database connection:

- `<DB>_HOST` — the database host.
- `<DB>_PORT` — the database port.
- `<DB>_USER` — the user name.
- `<DB>_PASSWORD` — the password.
- `<DB>_NAME` — the database name.

A platform connector injects these variables at runtime. The source code must not store these
variables. The configuration files must not store these variables.

## Environment Prerequisites

The database driver package must be installed. The database user must have rights to create its
schema on first startup. The database user must have rights to create and alter tables inside that
schema. The host must have network access to the database.

## Generic Code Example

```python
import psycopg
from psycopg_pool import ConnectionPool

_pool = None


def init_pool(config):
    """Create the pool at startup; return None when unconfigured or unavailable."""
    global _pool
    if not config.DB_HOST:
        return None  # persistence disabled; the application still starts

    conninfo = psycopg.conninfo.make_conninfo(
        host=config.DB_HOST,
        port=config.DB_PORT,
        dbname=config.DB_NAME,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        connect_timeout=5,
    )

    try:
        _pool = ConnectionPool(conninfo, min_size=1, max_size=5, open=True)
        return _pool
    except Exception:
        return None  # persistence disabled; never crash the process


_MIGRATION_LOCK_KEY = 1_234_567_000


def run_migrations(pool, migrations):
    """Apply pending migrations once, under one advisory lock."""
    try:
        with pool.connection() as conn:
            with conn.transaction():
                with conn.cursor() as cur:
                    cur.execute("SELECT pg_advisory_xact_lock(%s)", (_MIGRATION_LOCK_KEY,))
                    for version, sql, checksum in migrations:
                        if is_already_applied(cur, version, checksum):
                            continue
                        cur.execute(sql)
                        record_applied(cur, version, checksum)
        return True
    except Exception:
        return False  # persistence disabled; the caller must not raise


def write_through_mirror(pool, mode, payload):
    """Mirror in-memory working state to the database; never raise on failure."""
    try:
        with pool.connection() as conn:
            with conn.transaction():
                replace_mirrored_rows(conn, mode, payload)
    except Exception as exc:
        log_warning("mirror write failed", exc)  # in-memory change still stands
```

## Error Handling Rules

Owned records and mirrored working state fail differently. Do not mix the two rules.

**Owned records** (data the database alone holds):

- The application must return a clear error, for example HTTP 503, when the database is absent.
- The application must return the same error when the database is unreachable.
- The application must not use stale data after an error.

**Mirrored working state** (data the in-memory store also holds):

- A mirror write failure must not fail the request that triggered it.
- A mirror write failure must not crash the application.
- A mirror write failure must set a warning status. A health endpoint should report this status.
- The user interface should show a warning on a mirror write failure.
- The in-memory change always stands, even after a mirror write failure.

## Fallback Rule

Mirrored working state has no fallback source. The in-memory runtime store is always the primary
source; the database only mirrors it and never replaces it. Owned records have no fallback either.
When the database is absent, endpoints for owned records stay unavailable.

## Security Rules

Do not store credentials in the source code. Do not store credentials in configuration files
inside the repository. Store credentials only in the runtime environment. Use a platform connector
to inject credentials. Never log credentials.

## Skill Requirements

The skill must help the assistant with the following tasks.

1. Explain the connection principle in this document.
2. Add a new migration at the end of the migration list. Never edit an existing migration.
3. Add a new mirrored table in the correct place. Add validation for its rows. Add quarantine
   handling for rows that fail validation.
4. Reject any change that stores credentials in the repository.
5. Reject any change that lets a mirror write failure crash the process or fail a request.
6. Reject any change that returns stale data for owned records after a persistence error.
7. Keep the in-memory runtime store as the single source of truth for mirrored working state. The
   database only mirrors this data.
8. Keep owned-record writes inside their lifecycle. Never add a hard delete where archiving should
   apply instead.
