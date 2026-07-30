
# Flask template

For lean, server-rendered websites. Read this before planning or writing a Flask
app. It covers conventions only; dependency versions are not pinned here (on
CodeNow they come from the component's `requirements.txt`, which can change - see
`codenow.md`).

## Structure

The app is rooted in `src/`, built on top of the component's existing
`src/app.py` (which already wires `/` and `/health` - extend it, don't replace
it; see `codenow.md`). Organize `src/` into:

- `src/core/` - the Python backend, in three layers. Start minimal and add a
  layer only when the app needs it:
  - **routes** - Flask blueprints and route functions. Thin: read the request,
    call a service, return a response (`render_template` or `jsonify`). No
    business logic here.
  - **services** - the actual work, as plain Python with no Flask imports, so it
    is unit-tested directly.
  - **models** - the shapes of your data (dataclasses, or ORM models with a
    database). Add only when there is a real entity to model.

  Begin as single files (`core/routes.py`, `core/services.py`); split a layer
  into a package (`routes/`, `services/`) only once there are several feature
  areas.
  Import within `src/` without a `src.` prefix - `from core.routes import ...`
  in `app.py`, `from .services import ...` inside `core/routes.py`. CodeNow's
  runtime loads `app.py` as the top-level module `app` with `src/` itself as
  the path root; a `src.`-prefixed import resolves fine in tests and local runs
  (both put the repo root on the path) but crashes production with
  `ModuleNotFoundError: No module named 'src'`. `app.py` puts its own directory
  on `sys.path` at import time so this resolves the same way everywhere - keep
  that line if you touch the top of the file.
- `src/templates/` - Jinja HTML. One `base.html` that pages `extend`.
- `src/static/` - front-end assets in subfolders so nothing is loose:
  `static/css/` (stylesheets) and `static/js/` (scripts), plus `static/img/`
  only when the app actually has images. Keep all JavaScript in `static/js/`;
  for more than one script use ES modules (a single `<script type="module">`
  entry that imports the rest) rather than many loose `<script>` tags.
- `src/data/` - bundled, read-only data files. Never write runtime data here
  (see `codenow.md`).

Tests live in `tests/` at the project root, which the template already sets up -
do not rebuild it:

- `pytest.ini` sets `pythonpath = .`, so tests import as `from src.app import app`
  with no `PYTHONPATH=` prefix on any command. The import path is configured once,
  here.
- `tests/conftest.py` provides a `client` fixture wrapping Flask's test client.
- `tests/test_app.py` holds smoke tests for `/` and `/health` and for the B3
  tracing headers. These guard the CodeNow contract, so leave them in place and
  add your own tests alongside them.

## Conventions

- Keep `app.py` thin: create the app, load config and logging, register
  blueprints. Put the logic in `core/services`; keep routes thin.
- Use a blueprint per feature area once there is more than one; register them in
  `app.py`.
- Render pages with `render_template`; return JSON with `jsonify`. Keep logic out
  of templates.
- Reference assets with `url_for('static', filename=...)`.
- Treat invalid user input as a normal outcome (a bad form is not an error to
  log); see the logging rules in `codenow.md`.
- Use the built-in server (`app.run`) for local runs only; how the app is served
  in production is defined by the platform - do not change the exposed port.
  **Never pass `debug=True` in `app.py`.** Nothing in the repository defines how
  CodeNow starts the app, so it cannot be ruled out that the `__main__` block
  runs in production, where debug mode would expose the Werkzeug console. The
  auto-reloader is worth having locally, so `/spawn` takes it from the Flask CLI
  (`flask run --debug`) instead, and the file that ships carries no debug flag.

## Verify

Test the services directly with pytest, and exercise the routes with Flask's
test client (no live server needed). Boot the app once as a smoke check and
confirm `/health` still returns `{"status":"UP"}` on CodeNow.
