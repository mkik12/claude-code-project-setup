1. vymyslet název frameworku

## ai_bank_setup (the skills setup)

Built and verified statically; see `docs/5_ai_bank_setup.md` for the design and
the detail.

Settled, no further work: LibreOffice is out and `docx`, `pptx` and `xlsx` each
branch on whether `soffice` exists; `ldwh1` uses `oracledb` thin mode only; the
docx-js and pptxgenjs creation paths have verified python-docx and python-pptx
equivalents in each skill's `references/`; two Windows encoding bugs are fixed in
`office/validators/base.py` and `quick_validate.py`; `ste-lint.py` no longer
counts a possessive as a contraction or an en dash as an em dash; `docx` and
`pptx` ship `scripts/repack.py`, so the missing `zip` binary no longer stops the
unpack-edit-repack loop.

Open before it can be called equivalent to `flask_template`:

- Run a live session in a real project and confirm all eight skills trigger on
  the right prompt and do not catch each other's work. `ldwh1` against
  `app-database` is the pair to watch.
- Open a generated `.docx` and `.pptx` in Word and PowerPoint once. Both pass
  every schema check, but with no renderer on the machine nobody has looked at
  one.
- `.github/` mirror not started. Copilot has no on-demand skill mechanism, so
  decide between always-on `applyTo` instructions and dropping the skills there.

## GitHub Copilot side

`.github/` in `flask_template/` now mirrors `.claude/` (see
`docs/3b_copilot_workflow.md` for the mechanics). Not yet verified in a live
session - open items before treating it as equivalent to the Claude Code side:

- Run a real `/start` in VS Code and confirm `planner`/`coder` actually delegate
  in isolation (subagent invocation for custom agents is documented as
  experimental) and that their reports do not leak into the visible chat.
- Confirm `.claude/` and `.github/` coexisting in one project does not cause VS
  Code to load both sets of agents/instructions for a single Copilot session.
- Confirm the `tools: ['search', 'usages']` list on `planner.agent.md` actually
  excludes edit/terminal tools in the live Tools picker; adjust if the toolset
  names differ.
- Handbook: `handbook/2b GitHub Copilot.md` is still an empty placeholder.

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
