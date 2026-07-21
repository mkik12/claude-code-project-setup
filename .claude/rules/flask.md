
# Flask template

For lean, server-rendered websites. Read this before planning or writing a Flask
app. It covers conventions only; dependency versions are not pinned here (on
CodeNow they come from the component's `requirements.txt`, which can change - see
`codenow.md`).

## Structure

The app is rooted in `src/` (the entry point is `src/app.py`). Organize it into:

- `src/templates/` - Jinja HTML. One `base.html` that pages `extend`.
- `src/static/` - CSS and JavaScript (and images).
- `src/core/` - the Python backend (routes, services, models), split into
  modules.
- `src/data/` - bundled, read-only data files. Never write runtime data here
  (see `codenow.md`).

## Conventions

- Keep `app.py` thin: create the app, load config and logging, register
  blueprints. Put real logic in `src/core/`.
- Use a blueprint per feature area once there is more than one; register them in
  `app.py`.
- Render pages with `render_template`; return JSON with `jsonify`. Keep logic out
  of templates.
- Reference assets with `url_for('static', filename=...)`.
- Treat invalid user input as a normal outcome (a bad form is not an error to
  log); see the logging rules in `codenow.md`.
- Use the built-in server (`app.run`) for local runs only; how the app is served
  in production is defined by the platform - do not change the exposed port.

## Verify

Start the app locally, request the relevant page or route, and confirm it
returns the expected content (and that `/health` still returns `{"status":"UP"}`
on CodeNow). Add pytest tests that exercise each route.
