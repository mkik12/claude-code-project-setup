
# Flask

For a lean, server-rendered website. This file covers the conventions of a Flask
application. It pins no dependency version. On CodeNow the versions come from
the component `requirements.txt`, which can change. See `codenow.md`.

## Structure

The application sits in `src/`, on top of the component `src/app.py`. That
file wires `/` and `/health` already. Extend it, do not replace it.

Organize `src/` like this:

- `src/core/` - the Python backend, in three layers. Start with the minimum, and
  add a layer only when the application needs it.
  - **routes** - Flask blueprints and route functions. Keep them thin: read the
    request, call a service, return a response with `render_template` or
    `jsonify`. No business logic here.
  - **services** - the work itself, as plain Python with no Flask import. A unit
    test then calls it directly.
  - **models** - the shapes of your data, as a dataclass or as an ORM model. Add
    one only when there is a real entity to model.
- `src/templates/` - Jinja HTML. One `base.html` that each page extends.
- `src/static/` - front-end assets in subfolders, so nothing is loose.
  `static/css/` holds the stylesheets and `static/js/` holds the scripts. Add
  `static/img/` only when the application has images.
- `src/data/` - bundled, read-only data files. Never write runtime data here.
  See `codenow.md`.

Start a layer as a single file, such as `core/routes.py`. Split it into a
package only when there are several feature areas.

### The import prefix that breaks production

Import inside `src/` without a `src.` prefix. Write `from core.routes import ...`
in `app.py`, and `from .services import ...` inside `core/routes.py`.

The CodeNow runtime loads `app.py` as the top-level module `app`, with `src/` as
the path root. A `src.`-prefixed import works in a test and in a local run. Both
put the repository root on the path. In production the same import raises
`ModuleNotFoundError: No module named 'src'`. `app.py` puts its own directory on
`sys.path` at import time, so one spelling works everywhere. Keep that line if
you touch the top of the file.

## Tests

Tests live in `tests/` at the project root. The scaffold creates all three files
below, so do not build them again.

- `pytest.ini` sets `pythonpath = .`. A test imports with `from src.app import
  app`, and no command needs a `PYTHONPATH=` prefix.
- `tests/conftest.py` holds a `client` fixture around the Flask test client.
- `tests/test_app.py` holds the smoke tests for `/`, for `/health` and for the
  B3 tracing headers. These guard the CodeNow contract. Leave them in place and
  add your own tests next to them.

## Conventions

- Keep `app.py` thin. It creates the application, loads the config and the
  logging, and registers the blueprints. The logic belongs in `core/services`.
- Use one blueprint for each feature area once there is more than one. Register
  them in `app.py`.
- Render a page with `render_template`. Return JSON with `jsonify`. Keep the
  logic out of the template.
- Point to an asset with `url_for('static', filename=...)`.
- Treat invalid user input as a normal outcome. A bad form is not an error to
  log. See the logging rules in `codenow.md`.
- Use the built-in server (`app.run`) for a local run only. The platform defines
  how it serves the application in production. Do not change the exposed port.

**Never pass `debug=True` in `app.py`.** Nothing in the repository defines how
CodeNow starts the application, so the `__main__` block can run in production.
Debug mode there opens the Werkzeug console to the world. The auto-reloader is
worth having locally, so take it from the Flask CLI with `flask run --debug`.
The file that ships carries no debug flag.

## Verify

Test a service directly with pytest. Exercise a route with the Flask test
client, which needs no live server. Boot the application one time as a smoke
check, then confirm that `/health` still answers `{"status":"UP"}`.
