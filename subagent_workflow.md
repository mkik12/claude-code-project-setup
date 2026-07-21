
# What do we need to create

This document describes the agentic workflow for the framework: the roles, the
commands that drive a session, how memory is stored, and how verification and
commits work.

## Roles

The **main Claude Code session is the brain.** There is no orchestrator
subagent - the main session runs the workflow, handles every interaction with
the user, delegates to subagents, verifies results, and commits. Subagents run
in isolated context and return a single report; they never talk to the user
directly, so anything that needs a question or a confirmation goes back through
the main session.

There is no separate asker or parser subagent. Intake questions are asked by the
main session during `/initialize`, and Claude reads images and documents
natively.

Two subagents:

- **planner** (proposes; does not write production code)
  - turns a user request into a concrete plan for the coder
  - on first setup: proposes the scaffolding (which CodeNow component, when the
    project publishes to CodeNow) and the architecture template (Flask, FastAPI,
    or Dash)
  - if it needs a clarification or a decision (e.g. the architecture choice), it
    returns the questions to the main session, which asks the user and
    re-invokes the planner with the answers
- **coder** (implements the plan)
  - writes the code the planner specified, and writes the tests for it
  - works in Python, HTML, CSS, and plain JavaScript - no JS frameworks
  - verifies its own work: runs the tests and pylint, and fixes failures in a
    bounded loop before reporting
  - respects the CodeNow contract in CLAUDE.md (the `/health` endpoint, the
    exposed port, CI, logging, and no runtime writes to the app directory)
  - reports what it did, or that it is stuck, to the main session

Both subagents inherit the model the user chose for the session - do not
hardcode a model in their definitions.

## Scaffolding and architecture

These are two distinct choices at `/initialize` - the planner proposes each and
the user confirms (yes/no):

- **Scaffolding** (CodeNow only) - which CodeNow component the repository is
  created from. The component ships a Kubernetes scaffold and an `app.py` with
  index and health endpoints, but not the app architecture. Off CodeNow there is
  no scaffolding step.
- **Architecture** (always) - one of three templates, which defines the app's
  structure. Each template's spec lives in `rules/` (folder layout, dependencies,
  how to verify it); the planner and coder read the chosen one on demand:
  - **Flask** - lean websites. Layout: `static` (css + js), `templates` (html,
    with a `base.html` when useful), `data` (data files), `core` (Python
    backend).
  - **FastAPI** - fast backends.
  - **Dash** - interactive dashboards.

Either way the component does not provide the app architecture - the planner and
coder build it.

## Commands

The lifecycle is driven by explicit slash commands, not by the model guessing
intent. Anything the user types that is not a command is treated as work.

- **/start**
  - loads CLAUDE.md and session memory
  - reads the **Initialized** field in CLAUDE.md's "## Project status" block
    - if `no`: tell the user to run `/initialize`, then stop
    - if `yes`: greet the user, briefly explain what the assistant does, and wait
      for input
- **/initialize** (run once, when the project is new)
  - the main session asks the intake questions in `.claude/project-intake.md`
    (project description, input materials, publish to CodeNow?, who commits, how
    involved the user wants to be) and records the answers there
  - the planner proposes the scaffolding (CodeNow only) and the architecture
    template; the main session asks the user to confirm each (yes/no) and
    re-plans on "no"
  - the main session waits for a repository link and brings it into the working
    directory (the same folder as `.claude/`; the command file spells out the git
    technique, since `git clone` refuses a non-empty directory):
    - publishing to CodeNow: the user creates the repo in CodeNow from the chosen
      component and pastes the link
    - not publishing to CodeNow: the user pastes a link to some (empty) git repo
  - fills the "## Project status" block (Initialized: yes, template, CodeNow,
    repository, commit owner) and writes the "## Overview" in CLAUDE.md
  - then flows straight into the first work round - the planner and coder build
    the initial app structure (folder layout and a running skeleton)
- **/publish** (CodeNow only)
  - pushing code to the CodeNow repo does not deploy it; publishing is a manual
    step in CodeNow that this command walks the user through
  - pre-flight (the assistant checks first, and refuses to proceed on failure):
    everything committed and pushed, tests green, linter clean, the app runs
    locally and `/health` responds
  - then guides the user through CodeNow's manual publish steps
  - after the user confirms, verifies the live deployment responds
- **/document** (stub for now)
  - will generate project documentation; not implemented yet
- **/end**
  - updates the CLAUDE.md overview
  - updates the rolling session-memory summary
  - commits outstanding work per the commit rule
  - says goodbye; the user can close the session and start another one later

## Memory

- **CLAUDE.md** - the always-loaded operating file: a "## Project status" block
  (including the `Initialized` field), the frozen "## How this assistant works"
  section, and a "## Overview" of the project. Detailed conventions live in
  `.claude/rules/` and load on demand. Keep it around 300 lines. The status and
  overview are updated at `/initialize` and `/end`, never after individual coding
  tasks.
- **.claude/session-memory.md** - a rolling summary of what was done across
  sessions: recent sessions in detail, older ones compressed to a line. Loaded
  at `/start`, updated at `/end`. This keeps context small no matter how many
  sessions accumulate.
- there is **no per-agent memory**. Subagents keep nothing across runs; all
  durable state lives in CLAUDE.md and session memory.

Subagents cannot see these files unless told to. When a subagent needs context,
the main session either pastes it into the delegation prompt or instructs the
subagent to read the file as its first step.

## Verification

"It works" means the app loads and returns the expected result when it should
return something. The coder writes tests for the work, then verifies before
reporting.

The fix loop:

- the **coder** owns the inner loop: implement, write tests, run the tests and
  pylint, and if anything fails, fix, repeating up to 3 attempts
- if it is still failing after 3 attempts, the coder reports that it is stuck;
  the **main session** owns the outer decision: send it back to the planner to
  re-plan, ask the user, or stop
- neither retries forever, and the coder never silently gives up

## Commits

- commit when significant work has been done
- the commit owner is chosen at `/initialize`: if the user commits, tell them
  what to commit; otherwise the assistant commits
- keep commit messages short; `Co-authored-by: Claude` is fine (matches the
  global config)

## The `.claude` template

The `.claude/` folder is a template copied into each new project. Once copied, a
project's copy is **frozen** - improvements to the master template do not
propagate to projects that already copied it.

## Workflow rounds

First-time setup:
~~~
/start (not initialized) → tell user to run /initialize
/initialize → interview (project-intake)
            → [if CodeNow: planner proposes scaffolding → user confirms]
            → planner proposes architecture template → user confirms
            → user provides repo link → bring repo into the working folder
            → fill Project status (Initialized: yes) + Overview
            → planner + coder build the initial app skeleton
~~~

Normal work round (mid-session):
~~~
user request → planner (plan; clarify via main session if needed)
             → coder (implement + verify + bounded fix loop)
             → main session (commit if significant, report to user)
             → wait for next input
~~~

Publishing to CodeNow:
~~~
/publish → pre-flight (committed + pushed, tests, linter, local run, /health)
        → walk the user through CodeNow's manual publish steps
        → verify the live deployment responds
~~~

Ending a session:
~~~
/end → update CLAUDE.md + session-memory → commit if needed → goodbye
~~~
