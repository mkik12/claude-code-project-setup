
# CodeNow

Read this before any work when the project publishes to CodeNow (Project status:
"Publishes to CodeNow: yes"). It is the single home for CodeNow guidance: what a
component gives you, the contract you must not break, and the operational rules.

## What the component provides

Creating a repository from a CodeNow component scaffolds:

- `.codenow.yaml` - CI and runtime config: the base image, the CI pipelines, and
  the exposed `port` with an external endpoint. Do not repurpose it.
- `src/app.py` - the entry point, with `/` and a `/health` endpoint already
  wired and B3 tracing headers (`X-B3-*`) propagated on responses.
- `codenow/config/` - `config.yaml` and `log-config.json` (JSON logging via
  python-json-logger, loaded with `logging.config.dictConfig`).
- `requirements.txt`, `.gitignore`, `sonar-project.properties`, and `.run/`.
- a mostly empty `src/` - the app architecture is yours to build.

The component does not give you the app structure. Build it on top, additively,
following the chosen template rule.

## Change the scaffolding, but not its functionality

- **You may edit scaffold files when the app needs it, without asking.** For
  instance, the application's logging will require changing the provided logging
  configuration, and that is expected.
- **Don't change what the scaffolding does for the platform.** Keep the CodeNow
  contract working as provided: the CI pipelines, base images, exposed port,
  tracing headers, and the `/health` endpoint. Adapt what the app must; don't
  remove or repurpose what the platform relies on.
- **Prefer additive changes.** Build the application on top of the scaffold and
  follow the patterns it already establishes, rather than restructuring it.

## Contract - keep these working

- the `/health` endpoint (returns `{"status":"UP"}`, 200); CI and traffic
  routing depend on it.
- the exposed port and external endpoint in `.codenow.yaml`.
- the CI pipelines and base images.
- B3 tracing header propagation on responses.

## Dependencies

`requirements.txt` is provided by the component and its pins can change. Read it
from the repo; never hardcode versions in code or rules. Add a dependency only
when the app needs it, and record it in `requirements.txt`.

## Log operational failures, not user mistakes

- **Log what an operator must act on.** Failed calls to external services
  (connection refused, timeouts, DNS or TLS/certificate errors), database
  read/write failures, missing or unreadable configuration, dependency outages,
  and any unexpected exception. Use ERROR, or WARNING for transient or retried
  conditions, and always include the underlying cause (the real exception), not
  just the message shown to the user.
- **Don't log expected user input errors.** An invalid file type, empty upload,
  missing required field, malformed input, or a not-found for a user-supplied id
  are normal handled outcomes; logging them is noise.
- **Never swallow an operational failure silently** - catching it and only
  returning a message to the user, with nothing logged, hides the problem.
- **Keep module loggers alive.** When configuring logging via `dictConfig`, set
  `disable_existing_loggers` to false so loggers created at import time are not
  silenced.

## Never write runtime data into the application directory

- **The app directory may be read-only at runtime.** Don't create or write
  mutable files - a database, cache, uploads, or file logs - inside it; doing so
  fails when the filesystem is read-only (for example, SQLite then reports
  "unable to open database file").
- **Put writable state somewhere guaranteed writable and configurable.** Resolve
  the path from an environment variable, defaulting to a system temp directory,
  and use a mounted persistent volume when the data must survive restarts.
- **Keep read-only assets in the app directory.** Bundled lookup tables,
  templates, and static files belong there; writable state does not.

## Quality gates

CI runs pylint, pytest with coverage (written to `coverage.xml`), and SonarQube.
Keep pylint clean and tests green before pushing. A push does not deploy - the
user publishes manually (see `/publish`).
