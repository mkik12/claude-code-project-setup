# Connection to LDWH1 Data Warehouse

## Purpose

This document describes the connection to LDWH1. LDWH1 is the main data warehouse of the bank. This document is a generic specification. Use it to build a skill for Claude or GitHub Copilot.

## Connection Principle

The application reads pricing data from an Oracle database. The database name is LDWH1. The application uses the `oracledb` driver in thick mode. Thick mode needs the Oracle Client libraries on the host.

The application creates the connection at request time. The application does not create the connection at startup. The application opens one read-only transaction. The application reads all required views inside this one transaction. This method keeps the data consistent between views.

The application reads only from approved views. The application does not read from base tables. The application does not write to the database.

The application normalizes the raw rows into one internal data model. The internal data model does not depend on the source. A backup source, for example a local file, must produce the same data model.

The application stores the normalized data in a cache. The cache has a time limit. The time limit is a configurable number of seconds.

## Required Environment Variables

The application reads three variables for the database connection:

- `<DB>_DSN` — the connection string.
- `<DB>_USER` — the user name.
- `<DB>_PASSWORD` — the password.

A platform connector injects these variables at runtime. The source code must not store these variables. The configuration files must not store these variables.

The application reads one variable to enable the connection:

- `DWH_ENABLED` — set this variable to `True` to enable the database source. Set this variable to `False` to use the backup source.

The application reads one variable to control the cache:

- `CACHE_SECONDS` — the number of seconds before the cache expires.

## Environment Prerequisites

The host must have the Oracle Client libraries. The database user must have `SELECT` rights on all required views. The host must have network access to the database.

## Generic Code Example

```python
import oracledb

_client_ready = False

def get_connection(config):
    """Create a database connection only when the feature is enabled."""
    if not config.DWH_ENABLED:
        raise RuntimeError("The database source is disabled.")

    required_vars = ["DB_DSN", "DB_USER", "DB_PASSWORD"]
    missing_vars = [name for name in required_vars if not getattr(config, name)]
    if missing_vars:
        raise RuntimeError(f"Missing variables: {', '.join(missing_vars)}")

    global _client_ready
    if not _client_ready:
        oracledb.init_oracle_client()
        _client_ready = True

    return oracledb.connect(
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        dsn=config.DB_DSN,
    )


VIEW_QUERIES = {
    "view_one": "SELECT column_a, column_b FROM schema_name.view_one",
    "view_two": "SELECT column_c, column_d FROM schema_name.view_two",
}


def load_data(config):
    """Read all approved views in one read-only transaction."""
    connection = get_connection(config)
    try:
        cursor = connection.cursor()
        cursor.execute("SET TRANSACTION READ ONLY")

        raw_data = {}
        for name, query in VIEW_QUERIES.items():
            cursor.execute(query)
            raw_data[name] = cursor.fetchall()

        return build_data_model(raw_data)
    except Exception as exc:
        raise RuntimeError("The data source is temporarily unavailable.") from exc
    finally:
        connection.close()


def build_data_model(raw_data):
    """Validate raw rows and convert them into the internal data model."""
    for name, rows in raw_data.items():
        if not rows:
            raise ValueError(f"The view {name} returned no rows.")
    # Add validation and mapping logic here.
    return raw_data
```

## Error Handling Rules

The application must return an error when the connection fails. The application must return an error when a view is missing. The application must return an error when a view returns incomplete data. The application must return an error when views return conflicting data.

The application must not use old cached data after an error. The application must not use default values after an error. The error must reach the user as a clear failure, for example an HTTP 503 response.

## Fallback Rule

The application may use a backup source when the database is disabled. A typical backup source is a local file, for example a spreadsheet. The backup source must produce the same internal data model as the database.

## Security Rules

Do not store credentials in the source code. Do not store credentials in configuration files inside the repository. Store credentials only in the runtime environment. Use a platform connector or a secrets manager to inject credentials.

## Skill Requirements

The skill must help the assistant with the following tasks.

1. Explain the connection principle in this document.
2. Add a new view query in the correct place. Add validation for the new data. Add a test for the new data.
3. Reject any change that stores credentials in the repository.
4. Reject any change that adds a silent fallback to old or default data after an error.
5. Keep all view reads inside one read-only transaction.
6. Keep the database source and the backup source separate. Keep both sources producing the same data model.
