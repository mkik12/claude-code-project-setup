
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
  - loads the operating file and session memory, greets the user, and mentions
    once how they can reduce permission prompts
  - reads the **Initialized** field in the operating file's "Project status"
    block
    - if `yes`: gives a one-line status summary and waits for input (no coding)
    - if `no`: sets the project up in the same session, with no separate command:
      asks the intake questions (language to speak, project description, input
      materials, who handles commits and pushes); reads the repository URL from
      the `origin` remote, since the folder is already a clone of the CodeNow
      repo and there is nothing to connect; fills the "Project status" block
      (Initialized: yes, language, repository, commits-and-pushes owner) and
      writes the "Overview"; then flows straight into the first work round where
      the planner and coder build the initial app skeleton, and the main session
      writes the README (name, owner, short overview, how to run, external
      resources)
- **spawn**
  - runs the app locally, in the venv and in the background, so the session stays
    usable, and captures the URL it prints on startup
  - verifies it responds before handing over a link
  - tells the user, in their language, the URL to open, what they should see, how
    to try it, and how to stop it
- **kill**
  - stops every process listening on the app's port - all instances, not just the
    most recent - using the OS-appropriate tool
  - safe no-op when nothing is running
- **end**
  - stops any running app
  - updates the operating file's overview and the README
  - updates the rolling session-memory summary
  - commits and pushes outstanding work per the commit rule
  - says goodbye; the user can close the session and start another one later

## Memory

- **the operating file** - always loaded, and the single source of truth for
  project state: a "Project status" block (the `Initialized` field, the language
  preference, and the repository and commits-and-pushes owner), a frozen "How
  this assistant works" section, and an "Overview" of the project. Detailed
  conventions live in separate rule files and load on demand. Keep it around 300
  lines. The status and overview are updated at start and end, never after
  individual coding tasks.
- **session-memory.md** - a rolling summary of what was done across sessions:
  recent sessions in detail, older ones compressed to a line. Loaded at start,
  updated at end. This keeps context small no matter how many sessions
  accumulate.
- there is **no per-agent memory**. Subagents keep nothing across runs; all
  durable state lives in the operating file and session memory.

Subagents do not see session memory or the intake file unless told to. When a
subagent needs that context, the main session either pastes it into the
delegation prompt or instructs the subagent to read the file as its first step.

## User preference

The **language** to speak is captured at start, recorded in Project status, and
honored every session (defaulting to English when unset). Updates are always kept
brief - short bullet points, not long explanations - while still surfacing
genuine questions, risks, and failures.

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

- **static assistant config** - the agent definitions, commands, rules, and
  permission settings. The assistant never edits these at runtime.
- **writable operating files at the project root** - the operating file,
  `session-memory.md`, and `project-intake.md`, which the assistant updates as it
  works. These sit at the root deliberately; see `4_things_to_look_out.md` for
  the protected-path reason why.
- **the CodeNow scaffold** - `src/app.py` with `/` and `/health`,
  `.codenow.yaml`, `codenow/config/`, `requirements.txt`, `.run/`, and so on, so
  a fresh clone is already a complete, runnable starting project.

The master copy of all three lives in `flask_template/` in the framework repo;
that is what the CodeNow component is built from. Once a project is created its
copy is **frozen** - improvements to the master template do not propagate to
projects created from an earlier version of the component.

## Workflow rounds

First-time setup (run inside a fresh clone of the CodeNow repo):
~~~
start (not initialized) → interview (project-intake)
                        → read the repo URL from the origin remote
                        → fill Project status (Initialized: yes) + Overview
                        → planner + coder build the initial app skeleton
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
end → stop the app → update the operating file + session-memory → commit and
      push if needed → goodbye
~~~
