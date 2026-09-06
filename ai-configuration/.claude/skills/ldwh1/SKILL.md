---
name: ldwh1
description: Use this skill for any work that reads LDWH1, the bank data warehouse on Oracle. Triggers include LDWH1, DWH, "the data warehouse", the oracledb driver, thick mode or thin mode, a warehouse view, a read-only transaction across several views, DWH_ENABLED, CACHE_SECONDS, a DSN, and a spreadsheet fallback for warehouse data. Use it to explain how the connection works, to add or change a view query, to add validation or a test for warehouse data, or to review a change that touches the warehouse. Do NOT use it for the application's own database, for persistence, for saved records, or for migrations. That work belongs to the app-database skill.
---

# LDWH1, the bank data warehouse

LDWH1 is the main data warehouse of the bank. It runs on Oracle. An application
reads from it. An application never writes to it.

## The connection principle

Seven rules define every read. Keep all seven.

1. **Read at request time, not at startup.** The application opens the
   connection when a request needs data. An import-time or startup connection
   can crash-loop the process before the health endpoint answers.
2. **One read-only transaction for all views.** Open the transaction with
   `SET TRANSACTION READ ONLY`, then read every view you need inside it. This
   keeps the data consistent between views. A second transaction can see a
   later state, and the two results then disagree.
3. **Approved views only.** Never read a base table. Never write.
4. **Normalize into one internal data model.** The model does not depend on the
   source. Routes and services read the model, never the raw rows.
5. **Cache the normalized data.** `CACHE_SECONDS` sets the lifetime.
6. **A feature flag controls the source.** `DWH_ENABLED` is `True` for the
   warehouse and `False` for the backup source.
7. **Fail loudly.** An error reaches the user as a clear failure, for example
   HTTP 503.

## Environment variables

A platform connector injects these at runtime. The repository stores none of
them, in source or in a configuration file.

| Variable | What it is |
| :--- | :--- |
| `<DB>_DSN` | the connection string |
| `<DB>_USER` | the user name |
| `<DB>_PASSWORD` | the password |
| `DWH_ENABLED` | `True` for the warehouse, `False` for the backup source |
| `CACHE_SECONDS` | seconds before the cache expires |

## Thin mode only

`oracledb` runs in two modes. This setup uses **thin mode**, and only thin mode.

Thin mode is pure Python and needs no Oracle Client library on the host. Connect
with nothing more than the credentials:

```python
import oracledb


def get_connection(config):
    """Open a thin-mode connection when the feature is enabled."""
    if not config.DWH_ENABLED:
        raise RuntimeError("The database source is disabled.")

    missing = [n for n in ("DB_DSN", "DB_USER", "DB_PASSWORD")
               if not getattr(config, n)]
    if missing:
        raise RuntimeError(f"Missing variables: {', '.join(missing)}")

    return oracledb.connect(
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        dsn=config.DB_DSN,
    )
```

**Never call `oracledb.init_oracle_client()`.** That call switches the driver
into thick mode, which needs the Oracle Client libraries on the host. The
CodeNow runtime image is a slim Python image and carries none, so the call fails
at runtime.

Thin mode reads a view without trouble. It does not cover every Oracle feature.
When a requirement truly needs thick mode, stop and tell the user. That is a
platform decision, not a code change.

## How to add a view

1. Add the query to the `VIEW_QUERIES` map, next to the others. Name the key
   after the view.
2. Add the mapping from its rows into the internal data model.
3. Add validation for the new rows. An empty result is an error, not an empty
   list.
4. Add a test for the new data, with the rows faked. The test needs no live
   database.
5. Run the tests and the linter.

```python
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
        raise RuntimeError("The data source is unavailable.") from exc
    finally:
        connection.close()
```

## Refuse these five changes

Say why, and offer the correct form instead.

1. **A credential in the repository.** Source, configuration file, test fixture,
   or log line. Credentials live in the runtime environment only.
2. **A silent fallback after an error.** Old cached data and default values are
   both wrong answers presented as right ones. The error must reach the user.
3. **A view read outside the shared transaction.** A second connection or a
   second transaction breaks consistency between views.
4. **A call to `init_oracle_client()`.** It selects thick mode, and the host
   has no Oracle Client. Thin mode is the only supported mode.
5. **A backup source with a different data model.** The spreadsheet fallback
   and the warehouse produce the same model, or the code that reads them
   forks.

## Errors to return

Return an error when the connection fails, when a view is missing, when a view
returns incomplete data, and when two views disagree. Log the underlying
exception, because an operator must act on it. Do not log a user input mistake.

## Verify

Test the mapping and the validation directly, with faked rows. No live database
is needed for either. Test the disabled path too: with `DWH_ENABLED` false the
application still starts and still serves the backup source.
