
# CodeNow

Read this before any work on an application. Every project that uses this
configuration publishes to CodeNow. This file is the single home for CodeNow
guidance: what a component gives you, the contract you must not break, and the
operational rules.

## What the component gives you

A repository created from a CodeNow component holds:

- `.codenow.yaml` - the CI and runtime config. It names the base image, the CI
  pipelines, and the exposed `port` with an external endpoint. Do not repurpose
  it.
- `src/app.py` - the entry point. It wires `/` and a `/health` endpoint, and it
  copies the B3 tracing headers (`X-B3-*`) onto every response.
- `codenow/config/` - `config.yaml` and `log-config.json`. The logs are JSON,
  through python-json-logger and `logging.config.dictConfig`.
- `requirements.txt`, `.gitignore`, `sonar-project.properties` and `.run/`.
- a mostly empty `src/`. The application architecture is yours to build.

The component does not give you the application structure. Build it on top,
additively, and follow `flask.md`.

## Change the scaffolding, but not its functionality

- **You may edit a scaffold file when the application needs it, and you need not
  ask first.** The application logging, for example, will need a change to the
  supplied logging config. That is expected.
- **Do not change what the scaffolding does for the platform.** Keep the CodeNow
  contract working as it came. Adapt what the application must. Do not remove or
  repurpose what the platform depends on.
- **Prefer an additive change.** Build the application on top of the scaffold,
  and follow the patterns it sets already. Do not restructure it.

## The contract: keep these working

- the `/health` endpoint. It returns `{"status":"UP"}` and 200. CI and the
  traffic routing both depend on it.
- the exposed port and the external endpoint in `.codenow.yaml`.
- the CI pipelines and the base images.
- the B3 tracing headers on every response.

## Dependencies

The component ships `requirements.txt`, and its pins can change. Read it from
the repository, and never hardcode a version in code or in a rule.

Add a dependency only when the application needs it. Then record it in
`requirements.txt`, pinned to an exact version, in the style that is there
already.

## Log an operational failure, not a user mistake

Log what an operator must act on:

- a failed call to an external service: a refused connection, a timeout, a DNS
  error or a TLS error
- a database read failure or write failure
- a missing or unreadable configuration file
- a dependency outage
- any unexpected exception

Use ERROR, or WARNING for a transient or retried condition. Always include the
underlying cause, which is the real exception. The message you show the user is
not enough.

Do not log an expected user input error. An invalid file type, an empty upload,
a missing required field, malformed input, and a not-found for a user-supplied
id are all normal outcomes. To log them is noise.

**Never swallow an operational failure.** A catch that only returns a message to
the user, and logs nothing, hides the problem.

**Keep the module loggers alive.** When you configure logging with `dictConfig`,
set `disable_existing_loggers` to false. Otherwise a logger created at import
time goes silent, with no error anywhere.

## Never write runtime data into the application directory

- **The application directory can be read-only at runtime.** Do not create or
  write a mutable file there - a database, a cache, an upload, or a file log. It
  works locally and fails after the deploy. SQLite then reports "unable to open
  database file".
- **Put writable state in a place that accepts a write.** Resolve the path from
  an environment variable, and default to a system temp directory. Use a mounted
  persistent volume when the data must survive a restart.
- **Keep a read-only asset in the application directory.** A bundled lookup
  table, a template and a static file belong there. Writable state does not.

## Quality gates

CI runs pylint, then pytest with coverage into `coverage.xml`, then SonarQube.
Keep pylint clean and the tests green before you push. A push does not deploy.
The user publishes manually in CodeNow.
