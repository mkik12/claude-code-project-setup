
# Dash template

For interactive dashboards. Read this before planning or writing a Dash app.
Conventions only; dependency versions are not pinned here (see `codenow.md`).

## Structure

Rooted in `src/` (entry point `src/app.py`, exposing `app` and `app.server` -
the underlying Flask server the platform runs). Organize it into:

- `src/core/` - the backend: `layout/` (page and component layouts),
  `callbacks/` (interactivity), and data-loading helpers.
- `src/assets/` - Dash auto-serves CSS and JavaScript placed here.
- `src/data/` - bundled, read-only data files.

## Conventions

- Keep `app.py` thin: build the app, set `app.layout`, register callbacks.
- Split layout and callbacks into modules under `src/core/`; do not put
  everything in `app.py`.
- Give components stable `id`s; keep callback signatures small and pure.
- Load data through helper functions so callbacks stay about interaction, not
  I/O. Never write runtime data into the app directory (see `codenow.md`).
- Expose `app.server` so the platform can serve the app, and add the `/health`
  route on `app.server` when on CodeNow.

## Verify

Start the app locally, load the dashboard, and exercise the main interactions
(a control updates the expected output). Add pytest tests for the data and
callback helpers.
