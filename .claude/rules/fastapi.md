
# FastAPI template

For fast backends and APIs. Read this before planning or writing a FastAPI app.
Conventions only; dependency versions are not pinned here (see `codenow.md`).

## Structure

Rooted in `src/` (entry point `src/app.py`, exposing the ASGI `app`). Organize
it into:

- `src/core/` - the backend split into modules: `routers/` (endpoints),
  `models/` (Pydantic schemas), `services/` (logic).
- `src/data/` - bundled, read-only data files.
- add `src/templates/` and `src/static/` only if the API also serves HTML.

## Conventions

- Keep `app.py` thin: create the app, include routers, configure logging.
- One `APIRouter` per resource, grouped under `src/core/routers/`.
- Define request and response models as Pydantic classes; let FastAPI validate
  input and generate the OpenAPI docs.
- Use `async def` for I/O-bound endpoints and return typed responses.
- Return proper status codes; a validation error is a normal 4xx, not something
  to log (see `codenow.md`).

## Verify

Start the app locally and call each endpoint (a bad request returns 4xx, a good
one returns the expected body). Add pytest tests using FastAPI's `TestClient`,
and confirm `/health` still responds on CodeNow.
