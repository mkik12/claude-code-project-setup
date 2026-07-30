# Copilot framework - install into an existing CodeNow project

This adds a plan-and-code workflow to a CodeNow repository you already have. You
say what you want in plain language, a planner turns it into a plan, a coder
builds it and writes tests for it, and four commands drive the session:
`/start`, `/spawn`, `/kill`, and `/end`.

## Steps

1. **Copy the contents of this bundle into the root of your repository**, keeping
   the folder structure as it is here.
2. **Let it overwrite `src/app.py` and `codenow/config/log-config.json`.** Those
   two replace what the scaffold gave you, and the framework does not work
   correctly without them. Nothing else of yours is touched.
3. **Merge `.gitignore` into your existing one** rather than replacing it. The
   three lines that matter are listed below.
4. **Open the repository in VS Code.** Nothing needs enabling. VS Code finds the
   commands, the agents, and the rules on its own.
5. **Set the model picker to GPT-5.6 Luna** before you start work. This one
   matters more than it looks - see "Before you rely on it".
6. **Run `/start`** in Copilot Chat and answer the questions. It sets the project
   up and builds the first version in the same session.

From then on: describe what you want and it gets planned, built, and tested.
`/spawn` runs the app so you can click around, `/kill` stops it, and `/end` saves
the session and commits.

## The two files that replace the scaffold's

| File | Why |
| :--- | :--- |
| `src/app.py` | The stock version opens its log config as `'../codenow/config/log-config.json'`, a path that only resolves when the process starts inside `src/`. This framework starts the app from the project root, so with the stock file both `/spawn` and `pytest` die with `FileNotFoundError` before anything runs. This version resolves the path relative to `__file__` and works from either directory. It also clears the pylint failures that made the stock file score 6.82/10 and fail CI: an unused import, `open()` without an encoding, a missing docstring, and no final newline. |
| `codenow/config/log-config.json` | Adds `"disable_existing_loggers": false`. Without it, `dictConfig` silently switches off every logger created at import time, so any module doing `logger = logging.getLogger(__name__)` stops logging and nothing anywhere reports an error. |

The rest of your CodeNow scaffold is untouched and should stay as it is:
`.codenow.yaml`, `requirements.txt`, `codenow/config/config.yaml`,
`sonar-project.properties`, and `.run/` are all identical to what you already
have.

## The `.gitignore` lines

```
PROJECT.local.md
_migration/*
!_migration/.gitkeep
```

`PROJECT.local.md` holds your personal settings, which language the assistant
speaks to you and whether you or it does the commits. It stays out of git so
everyone on the project has their own.

`_migration/` is where `/start` asks you to put an existing app if you are moving
one onto the framework. Those lines keep its contents out of git, which matters
because a working app usually arrives with `.env` files, connection strings, and
data extracts in it. Without them, the first thing you drop in there is committed.

## What you get

- `PROJECT.md` - what the project is, shared with everyone. Written at `/start`.
- `session-memory.md` - a rolling summary across sessions, updated at `/end`.
- `tests/` and `pytest.ini` - a working test suite that passes on day one, so the
  quality gate never fails on code you did not write.
- `.github/` - the framework itself: the four commands, the two agents, and the
  Python, Flask, and CodeNow conventions they follow.

## Before you rely on it

**The model picker sets a ceiling.** The `planner` and `coder` agents pin their
own models, but a subagent may not exceed the main session's cost tier. If the
picker is on something cheaper than GPT-5.6 Luna, both quietly fall back to it
and your work runs on the wrong model with no warning. That is why step 5 is a
step and not a footnote.

**The pinned model ids are unverified against a live picker.** They use the
display-name format VS Code's documentation shows, for example
`GPT-5.6 Luna (copilot)`. An id that does not resolve falls back silently. On
your first session, check the names against your picker, and confirm by the
per-subagent AI credits readout rather than the hover label, which shows the
parent model even when the pin worked.

**There is no permission deny-list.** Nothing here blocks force-push, `rm -rf`,
`git clean`, or `git reset --hard`. Raise VS Code's permission level or set up
terminal auto-approval to whatever you are comfortable with, knowing that.

**The workflow is proven, this model assignment is not.** The framework has been
run end to end in a live Copilot session and worked, but on Claude Opus 5 rather
than on the models pinned here. So the commands, the agents, and the delegation
are known to work; what is new is which models they run on. If something behaves
oddly, switching the picker to a model you already trust is a fair first move,
and worth telling us about either way.
