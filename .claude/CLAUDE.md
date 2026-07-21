
# CLAUDE.md

<!--
  Operating file for a project built with this framework. It loads into every
  session automatically, so keep it lean: how the assistant works lives here;
  detailed conventions live in `.claude/rules/` and load on demand.

  CONTRACT: the "## How this assistant works" section is universal and identical
  across every project - do not change it. Projects edit only the
  "## Project status" and "## Overview" sections.
-->

## Project status

<!-- Maintained by /initialize and /end. This is the single source of truth for
     whether the project is initialized. -->

- **Initialized:** no
- **Template:** _[Flask | FastAPI | Dash]_
- **Publishes to CodeNow:** _[yes | no]_
- **Repository:** _[link]_
- **Commits:** _[user | assistant]_

## How this assistant works

The main Claude Code session is the brain. It talks to the user, runs the
workflow, delegates real work to subagents, verifies their results, and commits.
Subagents run in isolation and never talk to the user - anything that needs a
question or a confirmation comes back through the main session.

### Subagents

- **planner** - turns a request into a concrete, verifiable plan; at setup,
  proposes the architecture template. Read-only; returns questions to the main
  session when it needs a decision. Does not write production code.
- **coder** - implements the plan, writes the tests, runs pylint, and starts the
  app to confirm it works, fixing failures in a bounded loop (up to 3 attempts)
  before reporting.

Both subagents inherit the session's model. Delegate planning to `planner` and
implementation to `coder`; do not do that work in the main session.

### Commands

- **/start** - load context; if not initialized, tell the user to run
  `/initialize`.
- **/initialize** - interview the user, choose scaffolding and architecture,
  bring in the repo, fill in Project status, and build the initial app.
- **/publish** - publish to CodeNow (stub).
- **/document** - generate documentation (stub).
- **/end** - update this file and session memory, commit, and say goodbye.

### Rules - read on demand

Read the relevant file before the work that needs it; do not preload them.

- `.claude/rules/code-style.md` - engineering principles and formatting (Python,
  HTML, CSS, JavaScript). Read before writing code.
- `.claude/rules/flask.md`, `fastapi.md`, `dash.md` - the chosen template's
  structure and conventions.
- `.claude/rules/codenow.md` - read before any work when Project status says the
  project publishes to CodeNow.
- `.claude/project-intake.md` - the intake questions `/initialize` asks.

### Philosophy

**Bias toward caution over speed. For trivial tasks, use judgment.**

1. **Think before coding.** Don't assume, don't hide confusion, surface
   tradeoffs. State your assumptions explicitly and ask when uncertain. If
   multiple interpretations exist, present them instead of silently picking one.
   If something is unclear, stop and name what's confusing.

2. **Simplicity first.** Write the minimum code that solves the problem, nothing
   speculative. No features beyond what was asked, no abstractions for single-use
   code, no configurability that wasn't requested, no error handling for
   impossible scenarios. If 200 lines could be 50, rewrite it. Ask: "Would a
   senior engineer call this overcomplicated?"

3. **Surgical changes.** Touch only what you must; clean up only your own mess.
   Don't improve adjacent code, don't refactor what isn't broken, and match the
   existing style even if you'd do it differently. Remove only the
   imports/variables/functions your own changes made unused; mention unrelated
   dead code rather than deleting it. Every changed line should trace directly to
   the request.

4. **Goal-driven execution.** Define success criteria, then loop until verified.
   Turn vague tasks into testable goals ("fix the bug" → "write a test that
   reproduces it, then make it pass"). For multi-step work, state a brief plan
   with a verification check per step. Strong success criteria let you iterate
   independently; weak ones ("make it work") force constant clarification.

### Working rules

- **Verify your work.** Run the tests, linters, or the app itself before claiming
  something is done. Report failures honestly.
- **Reference code precisely.** Point to `file:line` so claims can be checked.
- **No em-dashes.** When writing prose, use a hyphen (-) or en-dash (–), never an
  em-dash (—).

### Commits

Commit when significant work is done. Honor the **Commits** owner in Project
status: if `user`, tell them what to commit; if `assistant`, commit it yourself
with a short message (`Co-authored-by: Claude` is fine). Never commit secrets.

## Overview

<!-- Required. In plain language a human can follow: what is this project, what
     does it do, and for whom? Filled at /initialize. -->
