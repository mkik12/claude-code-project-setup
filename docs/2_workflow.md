
# The workflow

This document describes the framework's design: the roles, the lifecycle that
drives a session, how memory is stored, and how verification and commits work.

It is deliberately assistant-agnostic. Everything here is true whichever coding
assistant runs the framework. How each one implements it - the file layout, the
agent definitions, the command mechanism, the permission model - lives in the
per-assistant documents:

- `3a_claude_workflow.md` - Claude Code (built).
- `3b_copilot_workflow.md` - GitHub Copilot (not built yet).

## Roles

The **main assistant session is the brain.** There is no orchestrator subagent -
the main session runs the workflow, handles every interaction with the user,
delegates to subagents, verifies results, and commits. Subagents run in isolated
context and return a single report; they never talk to the user directly, so
anything that needs a question or a confirmation goes back through the main
session.

There is no separate asker or parser subagent. Intake questions are asked by the
main session at the start of the first session, and the assistant reads images
and documents natively.

Two subagents:

- **planner** (proposes; does not write production code)
  - turns a user request into a concrete plan for the coder
  - at setup there is nothing to propose - the CodeNow component and the
    architecture are both fixed by which component the project was created from
  - if it needs a clarification or a decision, it returns the questions to the
    main session, which asks the user and re-invokes the planner with the answers
- **coder** (implements the plan)
  - writes the code the planner specified, and writes the tests for it
  - works in Python, HTML, CSS, and plain JavaScript - no JS frameworks
  - builds and runs inside a project virtual environment (venv), and records
    every installed dependency in `requirements.txt`, pinned
  - keeps generated and local files out of git via `.gitignore` (venv, caches,
    coverage, secrets, OS cruft); the pattern list lives in the code-style rule
  - verifies its own work: runs the tests and pylint, and fixes failures in a
    bounded loop before reporting
  - respects the CodeNow contract (the `/health` endpoint, the exposed port, CI,
    logging, and no runtime writes to the app directory)
  - reports what it did, or that it is stuck, to the main session

Both subagents inherit the model the user chose for the session. Do not hardcode
a model in their definitions.

A subagent's report is written for the main session, not for the user. A plan is a
work order for the coder: short, decided, no rationale for choices nobody
questioned, and no diagrams or code listings. The main session summarises it in a
few lines and surfaces only the decisions that need an answer. This is a context
constraint as much as a readability one - a subagent's final message lands in the
main session's context in full, and a plan is then passed on to the coder, so
length costs twice.

## Scaffolding and architecture

**Architecture** is fixed by which CodeNow component you create the repository
from - the framework ships one template per architecture, each its own component
and each with its own rule file:

- **Flask** - lean websites (this template).
- **FastAPI** - fast backends (a separate template).
- **Dash** - interactive dashboards (a separate template).

So the architecture is not chosen at setup; you pick it when you create the repo,
by choosing the component for the app you want.

**Scaffolding** is fixed too: each template ships as a CodeNow component, and
that component carries both the scaffold (the Kubernetes config and an `app.py`
with index and health endpoints, but not the app architecture) and this assistant
framework. So there is no scaffolding choice at setup either - the user creates a
repository from the matching component in CodeNow, clones it, and everything is
already in place; the planner and coder build the app on top.

## Session lifecycle

The lifecycle is driven by four explicit commands, not by the model guessing
intent. Anything the user types that is not a command is treated as work. Each
assistant document describes how its commands are invoked.

- **start**
  - does nothing when it has already run in the same session: it says so in one
    line and waits, rather than greeting a second time. The exception is a run
    the user interrupted mid-interview, which it resumes
  - greets the user, and mentions once how they can reduce permission prompts.
    `PROJECT.md` and session memory are already loaded, so there is nothing to
    fetch
  - checks two gates: **Initialized** in `PROJECT.md`, and whether this person has
    a `PROJECT.local.md`
    - both set: gives a one-line status summary and waits for input (no coding)
    - project set up but no `PROJECT.local.md`: asks that person only their
      language and commit preference, writes the file, then summarises status
    - project not set up: sets it up in the same session, with no separate command:
      asks the intake questions (see "Intake" below); reads the repository URL
      from the `origin` remote, since the folder is already a clone of the
      CodeNow repo and there is nothing to connect; fills the "Project status"
      block (Initialized: yes, repository) and writes the "Overview", with the
      language and commit owner going to `PROJECT.local.md`;
      then flows straight into the first work round where
      the planner and coder build the initial app skeleton, and the main session
      writes the README (name, owner, short overview, how to run, external
      resources)
- **spawn**
  - runs the app locally, in the venv and in the background, so the session stays
    usable, and captures the URL it prints on startup
  - does not start a second instance when one is already listening: it restarts
    that one if the app has changed since, and otherwise reuses it
  - verifies it responds before handing over a link
  - tells the user, in their language, the URL to open, what they should see, how
    to try it, and how to stop it
- **kill**
  - stops every process listening on the app's port - all instances, not just the
    most recent - using the OS-appropriate tool
  - safe no-op when nothing is running
- **end**
  - stops any running app
  - updates `PROJECT.md`'s overview and the README
  - updates the rolling session-memory summary
  - runs the tests and the linter once before committing anything, since this is
    the last point before the code reaches the repository where CI runs them
    anyway. On a failure it reports and asks rather than committing silently -
    work is sometimes deliberately left mid-flight
  - commits and pushes outstanding work per the commit rule
  - says goodbye; the user can close the session and start another one later

## Intake

Two things can be unset independently, and start checks both: whether the
**project** is set up (`Initialized` in `PROJECT.md`) and whether **this person**
is set up (`PROJECT.local.md` exists). That second gate is what makes the framework
work for a team. A colleague who clones a finished project has no
`PROJECT.local.md`, so they are asked their language and commit preference and
nothing else, and the project description is left alone.

The full interview runs only when the project itself is new. Language comes first,
so everything after it is in their language. Then a single question decides how the
project gets described, because users arrive in three quite different states:

- **(a) they know what they want.** They describe it; the assistant reads
  whatever they attach and summarises it back.
- **(b) they do not know yet.** The assistant works it out with them, offering
  concrete options rather than open questions. This is main-session work: the
  planner cannot talk to the user and stays technical. If it is still vague after
  a few rounds, the assistant proposes the smallest useful first version, so
  discovery cannot run forever with nothing built.
- **(c) they have a working app to move onto the framework.** The old app goes
  into a gitignored `_migration/` folder, so nothing in it can reach a commit
  before anyone has looked at it. The assistant then does three things in order:
  reports any secrets or data extracts it found, checks the app actually fits
  this template's architecture and lets the user choose what to do if it does
  not, and says what it thinks the app does. Migration means a **rewrite** onto
  the template's structure, reading the old files as the specification rather
  than keeping them. The subagents treat `_migration/` as read-only reference and
  must report any behaviour in it the specification does not account for, since a
  silently dropped feature is the main way a migration fails.

All three routes end the same way: the assistant writes a short summary of the
project, and the user has to confirm it before anything else happens. Users
rarely volunteer that they are satisfied, so the assistant offers the summary and
asks. That confirmed summary becomes the project overview, and in route (c) it is
the specification the rewrite works from.

Only then come the remaining questions: input materials, and who handles commits
and pushes.

## Memory

- **PROJECT.md** - always loaded, and the single source of truth for project
  state: a "Project status" block (the `Initialized` field and the repository) and
  an "Overview" of the project. Keep it under about 200 lines. Both sections are
  updated at start and end, never after individual coding tasks. This file belongs
  to the project rather than to any one assistant, so every assistant reads and
  writes the same state instead of keeping a private copy that can drift.
- **PROJECT.local.md** - one person's settings: which language the assistant
  speaks to them, and whether they or the assistant commits. **Gitignored**, so
  each person on a shared project has their own and nobody inherits a colleague's
  preferences. Not imported, because a gitignored file does not exist in a fresh
  clone; start reads it, and its absence is how the framework recognises someone
  new (see "Intake").
- **the assistant's own instruction file** - also always loaded, holding how that
  assistant works: the subagents, the commands, and the rules index. It is
  identical across every project and is never written at runtime, so it is static
  config rather than memory. Each assistant has its own; see `3a` and `3b`.
  Detailed conventions live in separate rule files alongside it.
- **session-memory.md** - a rolling summary of what was done across sessions:
  recent sessions in detail, older ones compressed to a line. Always loaded,
  updated at end, and held under 100 lines. One session is one entry, so an end
  that runs a second time revises its entry rather than appending another.
  Compressing the old entries is the only thing keeping context small no matter
  how many sessions accumulate.
- there is **no per-agent memory**. Subagents keep nothing across runs; all
  durable state lives in `PROJECT.md` and session memory.

Subagents do not see session memory or the intake file unless told to. When a
subagent needs that context, the main session either pastes it into the
delegation prompt or instructs the subagent to read the file as its first step.

## User preference

The **language** to speak is captured at start, recorded in `PROJECT.local.md`, and
honored every session (defaulting to English when unset). Updates are always kept
brief - short bullet points, not long explanations - while still surfacing
genuine questions, risks, and failures.

That setting governs **what the assistant says, and nothing else.** Everything
written stays in English: the code, the comments, the commit messages, and the
shared files (`PROJECT.md`, `session-memory.md`, `README.md`).
Two reasons. The work itself is already in English - the libraries, the error
messages, the rules - so translating it only adds a lossy step. And the shared
files are read by colleagues who may not speak the language the assistant is
speaking, which is exactly the case a per-person language setting creates. The
subagents never address the user at all, so they work wholly in English.

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

## Commits and pushes

- commit when significant work has been done, then push
- the owner is chosen at start: if the user owns them, tell them what to commit
  and push; otherwise the assistant commits and pushes itself
- keep commit messages short; a co-authorship trailer is fine. Never commit
  secrets, and never force-push

## What ships in a project

The framework reaches a project as part of the CodeNow component, so a repository
created from that component already contains all three parts:

- **static assistant config** - the instruction file, agent definitions,
  commands, rules, and permission settings. The assistant never edits these at
  runtime, and each assistant has its own set.
- **writable project files at the project root** - `PROJECT.md` and
  `session-memory.md`, which the assistant updates as it works and which are shared
  by every assistant and every person on the project. `PROJECT.local.md` sits
  alongside them but is gitignored and per-person. The read-only question script
  is not here at all: nothing writes to it, so it lives with the static config. They are
  at the root deliberately; see `4_things_to_look_out.md` for the protected-path
  reason why.
- **the CodeNow scaffold** - `src/app.py` with `/` and `/health`,
  `.codenow.yaml`, `codenow/config/`, `requirements.txt`, `.run/`, and so on, so
  a fresh clone is already a complete, runnable starting project.
- **a working test suite** - `pytest.ini`, `tests/conftest.py`, and smoke tests for
  the endpoints the platform depends on. A fresh clone passes pylint, pytest, and
  coverage before a line of app code is written, so the quality gate never fails on
  scaffold the user did not write.

The master copy of all three lives in `flask_template/` in the framework repo;
that is what the CodeNow component is built from. Once a project is created its
copy is **frozen** - improvements to the master template do not propagate to
projects created from an earlier version of the component.

## Workflow rounds

First-time setup (run inside a fresh clone of the CodeNow repo):
~~~
start (project not initialized) → language
                        → starting point: (a) knows / (b) unsure / (c) migrating
                        → route-specific conversation → confirmed summary
                        → input materials, commits owner
                        → read the repo URL from the origin remote
                        → fill Project status (Initialized: yes) + Overview
                        → planner + coder build:
                            (a)(b) initial app skeleton
                            (c)    rewrite onto the template structure
~~~

Normal work round (mid-session):
~~~
user request → planner (plan; clarify via main session if needed)
             → coder (implement + verify + bounded fix loop)
             → main session (commit and push if significant, report to user)
             → wait for next input
~~~

Running the app for the user:
~~~
spawn → start the app in the venv, in the background → verify it responds
      → give the user the URL and how to test it
kill  → stop all instances on the app's port
~~~

Ending a session:
~~~
end → stop the app → update PROJECT.md + session-memory → commit and
      push if needed → goodbye
~~~
