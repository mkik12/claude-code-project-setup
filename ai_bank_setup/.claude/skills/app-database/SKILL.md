---
name: app-database
description: Use this skill for any work on the application's own database, the one a platform connector provisions for it. Triggers include PostgreSQL, psycopg, a connection pool, persistence, saving or loading application data, a saved document or snapshot, a database migration, an advisory lock, a migration checksum, mirrored working state, hydrating an in-memory store at startup, a quarantined row, and an optimistic revision check. Use it to explain how persistence works, to add a migration, to add a mirrored table, or to review a change that touches the database. Do NOT use it for reads from LDWH1 or any bank data warehouse on Oracle. That work belongs to the ldwh1 skill.
---

# The application database

A platform connector provisions a PostgreSQL database for the application. The
application owns it. The application connects with a pool.

## Two kinds of data, two sets of rules

Decide which kind you are working with first. The error rules differ, and mixing
them is the main way this code goes wrong.

| | **Owned records** | **Mirrored working state** |
| :--- | :--- | :--- |
| Source of truth | the database | the in-memory runtime store |
| Examples | a saved document, a saved snapshot | live settings a request can change |
| On a write failure | return HTTP 503 | keep the change, set a warning |
| On the database being absent | the endpoint is unavailable | the application runs normally |
| Stale data after an error | never serve it | not applicable |

Pick one rule set for each kind of data. Do not mix them.

## The connection principle

1. **Open the pool in the app factory.** Small minimum size, small maximum
   size. Never open a connection at import time, because an import-time failure
   can crash-loop the process before the health endpoint exists.
2. **The database is optional.** The application starts without it. Every
   read-only path still works. A missing or broken connection disables
   persistence and nothing else.
3. **Never crash on a database problem.** An unconfigured or unreachable
   database returns no pool. The caller handles that, and the process lives.

`psycopg` and its pool are a new dependency. Pin them in `requirements.txt` at
the exact version you install, matching the pinned style already there.

```python
def init_pool(config):
    """Create the pool at startup; return None when unconfigured or down."""
    global _pool
    if not config.DB_HOST:
        return None  # persistence disabled; the application still starts

    conninfo = psycopg.conninfo.make_conninfo(
        host=config.DB_HOST, port=config.DB_PORT, dbname=config.DB_NAME,
        user=config.DB_USER, password=config.DB_PASSWORD, connect_timeout=5,
    )
    try:
        _pool = ConnectionPool(conninfo, min_size=1, max_size=5, open=True)
        return _pool
    except Exception:
        return None  # persistence disabled; never crash the process
```

## Migrations

Migrations run once, right after the pool opens.

- **One advisory lock holds them.** `pg_advisory_xact_lock` stops two replicas
  from migrating at the same time.
- **Each migration carries a checksum.** A changed checksum on a migration that
  already ran aborts the migrations and disables persistence. It never crashes
  the process.
- **Add a migration at the end of the list.** Never edit a migration that
  shipped. It ran already on some database somewhere, and editing it makes the
  two disagree in silence.

## Mirrored working state

The in-memory store is the truth. The database only mirrors it.

1. **Namespace the mirror** by a mode key or a tenant key. Each mode owns its
   rows.
2. **Write to the mirror after every change**, and never block the request on
   that write.
3. **Hydrate at startup**, over the in-memory defaults.
4. **Validate every hydrated row.** A row that fails validation goes to
   quarantine. It reaches neither the runtime store nor any calculation, and it
   stays in the mirror for an administrator to read.

## Environment variables

A platform connector injects these at runtime. The repository stores none of
them, in source or in a configuration file. Never log one.

`<DB>_HOST`, `<DB>_PORT`, `<DB>_USER`, `<DB>_PASSWORD`, `<DB>_NAME`.

An absent `<DB>_HOST` means persistence is off. That is a normal state, not an
error.

## Refuse these four changes

Say why, and offer the correct form instead.

1. **A credential in the repository.** Source, configuration file, test fixture,
   or log line. Credentials live in the runtime environment only.
2. **A mirror write failure that fails a request or kills the process.** It sets
   a warning status, the health endpoint reports it, and the in-memory change
   stands.
3. **Stale data served for an owned record after an error.** Return the error.
4. **A hard delete where the record has a lifecycle.** Archiving replaces it.
   Move the record to `archived`; do not remove the row.

## Verify

Test three paths, and all three run without a live database:

- **persistence disabled.** `<DB>_HOST` unset. The application starts and serves
  every read-only path.
- **a mirror write that fails.** The request still succeeds and the warning
  status is set.
- **a hydrated row that fails validation.** It is quarantined, and it reaches no
  calculation.
