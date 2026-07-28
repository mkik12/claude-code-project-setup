1. vymyslet název frameworku

## Changes made to the CI

The template now passes the CodeNow quality gate on a fresh clone. Before these
changes a brand-new project failed CI before anyone wrote a line of app code.

- **pylint was failing.** The component's `src/app.py` scored 6.82/10 and exited
  20: unused `requests` import, imports in the wrong order, `open()` without an
  encoding, a missing docstring on `health_check`, and no final newline. All fixed
  without changing behaviour. Now 10.00/10, exit 0.
- **pytest was failing.** The template shipped no tests, and pytest exits 5 on
  "no tests collected", which CI treats as a failure. Added `pytest.ini`
  (`pythonpath = .`, so the import path is set once), `tests/conftest.py` with a
  `client` fixture, and `tests/test_app.py` with smoke tests for `/`, `/health`,
  and the B3 tracing headers. Those cover the CodeNow contract, so a change that
  would break deployment fails in tests first.
- **Coverage produced nothing for SonarQube.** `sonar-project.properties` points
  Sonar at `coverage.xml`, which never existed because there were no tests.
  `coverage run -m pytest` now produces it: 98% overall, 96% on `src/app.py`.

Verified with the pinned versions from `requirements.txt` (pylint 3.2.3, pytest
8.2.2, coverage 7.5.4), and the app still boots with `/` and `/health` answering
and the B3 headers echoed.

### Still open on the CI side

- `waitress==3.0.0` is pinned but referenced nowhere in the template, and
  `.codenow.yaml` exposes port 80 while `app.py` binds 8080. Someone who knows the
  pipeline should confirm how the app is served in production, then document it in
  `.claude/rules/codenow.md`.
- `codenow/config/config.yaml` contains only `scaffolder: config: test`, which
  looks like scaffolder test data shipping into every project.
