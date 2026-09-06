You are picking up work on a reusable coding-assistant framework built at RBCZ.
Read this, confirm you understand, then wait for the task. Follow the repo's root
`CLAUDE.md`: think before coding, simplicity first, surgical changes, verify your
work, reference `file:line`, no em-dashes.

## What the framework is for

It turns a plain-language description of an application into a working Python web
app, for non-technical and technical colleagues alike. The user says what they
want; a **planner** turns it into a plan, a **coder** builds it and writes tests,
and the main session verifies and commits. Four commands drive a session:
`/start`, `/spawn`, `/kill`, `/end`. Anything else the user types is treated as
work.

The main session is the brain. It is the only thing that talks to the user.
Subagents run in isolated context, never address the user, and return a single
report that the main session summarises rather than pastes.

## What this repo is

The master/template repo. The first deliverable is `flask_template/`, which becomes a
**CodeNow component**. A colleague creates a repository from that component,
clones it, opens their assistant, and runs `/start`. Everything is already in
place; the framework ships inside the component rather than being installed.

- `flask_template/` - the first deliverable.
- `ai_bank_setup/` - the second deliverable and `flask_template`'s successor:
  a drop-in `.claude/` with no commands and no subagents, built on eight
  on-demand skills. Read `docs/5_ai_bank_setup.md` before touching it.
- `docs/` - the authoritative design spec, kept in sync with the template:
  - `1_goal.md` - why the framework exists.
  - `2_workflow.md` - the design, deliberately assistant-agnostic.
  - `3a_claude_workflow.md` - how Claude Code implements it.
  - `3b_copilot_workflow.md` - how GitHub Copilot implements it.
  - `4_things_to_look_out.md` - verified non-obvious behaviour, with sources.
    **Read this before touching permissions, logging, `.gitignore`, or anything
    that starts or stops the app.**
  - `5_ai_bank_setup.md` - the skills-based second deliverable, and every way
    it departs from `2_workflow.md`.
  - `copilot_model_audit_RESULT.md` - per-token model selection for the Copilot
    side, with rates verified against GitHub's docs.
- `CLAUDE.md` - the rules for working on *this* repo.
- `tasks.md` - open work, plus a record of the CI fixes.
- `handbook/` - the Czech user tutorial. Five files, all **empty**.
- `flowcharts/` - diagrams, **stale**, several design changes behind.
- `resources/scaffolding_example/` - the untouched reference CodeNow scaffold.
  Do not edit it; its only value is being unmodified. Diff against it to see
  exactly what the template changed.

## How flask_template is organised

The split is by **what gets written at runtime**, not by what a file is about,
because `.claude/` is a protected path where writes always prompt and cannot be
allow-listed.

**Static config, never written at runtime.** Two parallel trees, one per
assistant:

| Claude Code | GitHub Copilot |
| :--- | :--- |
| `.claude/CLAUDE.md` | `.github/copilot-instructions.md` |
| `.claude/intake.md` | `.github/intake.md` |
| `.claude/agents/{planner,coder}.md` | `.github/agents/*.agent.md` |
| `.claude/commands/{start,spawn,kill,end}.md` | `.github/prompts/*.prompt.md` |
| `.claude/rules/{code-style,codenow,flask}.md` | `.github/instructions/*.instructions.md` |
| `.claude/settings.json` | *no equivalent - see 3b* |

**Writable, at the project root:**

- `PROJECT.md` - committed and shared: `Initialized`, `Repository`, Overview.
- `PROJECT.local.md` - **gitignored, per person**: language, commit owner.
- `session-memory.md` - committed, rolling summary, under 100 lines.
- `README.md` - human-facing, five sections.

**Bundled CodeNow scaffold plus test suite:** `src/app.py` (`/`, `/health`, B3
tracing, file-relative log config, port 8080), `.codenow.yaml`, `codenow/config/`,
`requirements.txt` (pinned), `sonar-project.properties`, `.run/`, `.gitignore`,
`pytest.ini`, `tests/{conftest,test_app}.py`, `_migration/.gitkeep`.

## Decisions that are settled - do not re-litigate

- **The framework ships inside the CodeNow component.** `/start` does not connect
  a repo or run `git init`; it reads `git remote get-url origin` and stops if
  there is no remote.
- **`.claude/CLAUDE.md` imports `@../PROJECT.md` and `@../session-memory.md`.**
  The `../` is required, since import paths resolve relative to the importing
  file. Never instruct the assistant to read an imported file, and never hedge
  with "if it exists" - that triggers a Glob.
- **`PROJECT.local.md` is deliberately NOT imported.** A gitignored file does not
  exist in a fresh clone, so an import would point at nothing. Its absence is the
  "new person" gate instead.
- **`/start` checks two independent gates:** is the project set up
  (`Initialized`), and is this person set up (`PROJECT.local.md` exists). It also
  refuses to run twice in one conversation, except after `/end` or an interrupted
  interview.
- **Intake:** q1 language, then q2 picks one of three routes - (a) knows what
  they want, (b) unsure, work it out, (c) migrating a working app. All three
  converge on a summary the user must explicitly confirm; that becomes q2b, the
  Overview, and in route (c) the rewrite specification. Then q3 materials, q4
  commits.
- **Route (c) is a rewrite, not a port.** The old app goes in gitignored
  `_migration/`; secrets are named before anything is committed; an architecture
  mismatch is reported with both costs and the **user chooses**. Subagents treat
  `_migration/` as read-only and must report anything they could not account for.
  Never delete it - it may be the only copy.
- **Language governs only what is said.** All files, all reasoning, and both
  subagents work in English. Exception: user-visible strings in the app follow
  the plan.
- **Plans are work orders, under about 40 lines.** Never paste a subagent report
  to the user; summarise and surface only decisions needing an answer.
- **`session-memory.md` is one entry per session**, headed `## YYYY-MM-DD - Name`
  from `git config user.name`, and that heading survives compression.
- **No `debug=True` in `app.py`.** Nobody has confirmed how CodeNow starts the
  app, so it cannot be ruled out that the `__main__` block runs in production.
  `/spawn` takes the reloader from the Flask CLI instead.
- Architecture is fixed per template (Flask here; FastAPI and Dash would be
  separate components). CodeNow is always on.

## Where the two assistants deliberately differ

Everything is mirrored except three things, all documented in `3b`:

- **Model choice.** Claude subagents inherit the session model. Copilot subagents
  **pin** models, because Copilot bills per token and a subagent may not exceed
  the main session's cost tier. The main session's model is the VS Code picker,
  which no file can set, so `/start` asks the user for it.
- **Permissions.** Claude has `settings.json` allow/deny rules. Copilot has no
  shippable equivalent, so force-push, `rm -rf`, `git clean`, and
  `git reset --hard` are not blocked on that side.
- **Rule loading.** Claude rules load by default unless scoped with `paths`.
  Copilot instructions are the inverse: never applied without `applyTo`, so the
  Copilot files must set `applyTo: '**'` to get the same always-on behaviour.

## Verified, so do not re-derive

All documented with sources in `docs/4_things_to_look_out.md`. The ones that bite
hardest:

- `Bash(...)` and `PowerShell(...)` are separate rule namespaces, so every
  permission rule is written twice. PowerShell is primary on Windows.
- `permissions.allow` is inert until the user accepts the workspace-trust dialog,
  and protected paths cannot be allow-listed at all.
- A repository cannot grant itself `auto` mode.
- `acceptEdits` auto-approves `rm`, `mv`, `cp`, `sed`, and `Remove-Item`, which is
  why destructive commands are denied by name.
- `logging.config.dictConfig` defaults `disable_existing_loggers` to true and
  silently kills module loggers. Fixed in `log-config.json`.
- Git Bash rewrites `/F` into `F:/`, so `taskkill` must run through the
  **PowerShell tool**.
- The Flask reloader forks, and killing the parent leaves the child serving while
  `netstat` still names the dead parent. `/kill` has a fallback for this.
- `pytest` exits 5 when it collects no tests, which CI treats as failure.
- `_migration/*` plus `!_migration/.gitkeep`, never `_migration/` - git does not
  descend into an excluded directory.

## Current state

**Claude Code side: built and verified**, including end to end against a real
CodeNow repository.

**`ai_bank_setup/.claude/`: built.** Eight skills, three rules, permissions, and
a CLAUDE.md written in Simplified Technical English. Linted and validated, but
not yet exercised in a live session. Its `.github/` mirror does not exist.

**Copilot side: built, and run live once** - the commands, agents, and delegation
worked, but on Claude Opus 5 rather than on the models now pinned in
`.github/agents/*.agent.md`. That model assignment is the part not yet exercised.

**Template quality gate, re-verified in a clean venv with the pinned versions:**
`pytest` 3 passed, `coverage` 98% total and 96% on `src/app.py`, `pylint src tests`
10.00/10.

## Open items

1. **The pinned Copilot model ids are unverified** against a live picker. They use
   display-name format (`GPT-5.6 Luna (copilot)`); an id that does not resolve
   falls back silently, and the hover label shows the parent model either way.
   Verify by the per-subagent AI credits readout.
2. **`handbook/` is five empty files.** Owner says this is fine for now.
3. **`flowcharts/` are stale.** Owner will handle later.
4. **The framework name is unsettled.** `tasks.md` item 1 is still open.
5. **CodeNow questions nobody has answered:** `waitress` is pinned but referenced
   nowhere while `.codenow.yaml` exposes port 80 and `app.py` binds 8080, so how
   is the app served in production? Does CodeNow substitute the `.run/` project
   name placeholders? How is the component rebuilt from `flask_template/`, which
   decides how long a fix takes to reach new projects?
6. **`codenow/config/config.yaml` contains only `scaffolder: config: test`**,
   which looks like scaffolder test data shipping into every project.
7. **`requirements.txt` pins `requests`** but nothing imports it, same class of
   question as `waitress`.
8. **`docs/2_workflow.md:13` still says Copilot is "not built yet"**, which
   contradicts the README and `tasks.md`.

## How to work here

Read `docs/` in order first, then `flask_template/`, and confirm the current state
before changing anything. Keep the docs in sync with the template: `2_workflow.md`
is assistant-agnostic, `3a` and `3b` hold the per-assistant mechanics, and
`4_things_to_look_out.md` collects verified traps with sources - only add
something there once you have actually reproduced it.

**Change both assistants or neither.** A change to a command, agent, or rule on
one side needs its counterpart on the other, unless it is one of the three
documented divergences above.

Verify claims rather than asserting them, and say so when a check fails.
