
# CLAUDE.md

<!--
  TEMPLATE CONTRACT (do not change):
  Everything from "## How to basic" down to and including the "### Overview"
  heading is universal and identical across every project. Project repos MUST
  NOT edit it. A project may only:
    1. add content INSIDE "### Overview", and
    2. append new sections AFTER "### Overview".
-->

## How to basic

How Claude Code should work in this repository. These rules are universal and
apply before any project-specific guidance below.

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

### Technical principles

How Claude should write code, design, and structure the project.

#### Universal – every codebase

- **Names say what they mean.** Clear, descriptive names over clever or
  abbreviated ones. Match the conventions already in use.
- **Comments explain why, not what.** Match the surrounding comment density.
  Don't narrate code that speaks for itself; don't leave commented-out blocks.
- **Dependencies are a cost.** Prefer the standard library and existing
  dependencies. Ask before adding a new one.
- **Errors that can actually happen.** Handle realistic failure modes; don't
  guard against the impossible.
- **Never hardcode secrets.** No credentials, tokens, or keys in source or logs.
- **Frame every code file with blank lines.** Start and end each programming
  file with one empty line (not data files like `.csv`).
- **Verify your work.** Run the tests, linters, or the app itself before
  claiming something is done. Report failures honestly.
- **Reference code precisely.** Point to `file:line` so claims can be checked.
- **No em-dashes.** When writing prose, use a hyphen (-) or en-dash (–), never
  an em-dash (—).

#### New codebase (Python)

Apply when starting fresh, with no existing conventions to follow.

- **Naming.** `snake_case` for functions, variables, and modules; `PascalCase`
  for classes (e.g. Pydantic models and `Enum` classes); `UPPER_SNAKE_CASE` for
  module-level constants.
- **Docstrings.** Google style for modules and public functions. Private
  functions take a one-line docstring and a `_` name prefix.
- **Explicit imports.** No `from X import *`.
- **Two blank lines** between top-level function and class definitions (one
  blank line between methods), per PEP 8.
- **Early returns over deep nesting** – especially in node functions.
- **Fix typos at the source.** When you touch a symbol with a typo, rename it
  rather than propagate the mistake.
- **Line length.** Limit code lines to 79 characters. For flowing prose
  (docstrings, comments), limit to 72 characters.

#### Existing codebase

Apply when conventions are already established.

- **Match the codebase.** Follow the existing structure, naming, idioms, and
  formatting, even where they differ from the "New codebase" rules above.
  Consistency with the surrounding code beats personal preference.
- **When the conventions are unclear or inconsistent, ask** whether to apply the
  "New codebase" rules instead.

#### CodeNow

Apply to every project scaffolded with CodeNow.

##### Change the scaffolding, but not its functionality

- **You may edit scaffold files when the app needs it, without asking.** For
  instance, the application's logging will require changing the provided
  logging configuration, and that is expected.
- **Don't change what the scaffolding does for the platform.** Keep the
  CodeNow contract working as provided: the CI pipelines, base images, exposed
  port, tracing headers, and the `/health` endpoint. Adapt what the app must;
  don't remove or repurpose what the platform relies on.
- **Prefer additive changes.** Build the application on top of the scaffold
  and follow the patterns it already establishes, rather than restructuring
  it.

##### Log operational failures, not user mistakes

- **Log what an operator must act on.** Failed calls to external services
  (connection refused, timeouts, DNS or TLS/certificate errors), database
  read/write failures, missing or unreadable configuration, dependency
  outages, and any unexpected exception. Use ERROR, or WARNING for transient
  or retried conditions, and always include the underlying cause (the real
  exception), not just the message shown to the user.
- **Don't log expected user input errors.** An invalid file type, empty
  upload, missing required field, malformed input, or a not-found for a
  user-supplied id are normal handled outcomes; logging them is noise.
- **Never swallow an operational failure silently** - catching it and only
  returning a message to the user, with nothing logged, hides the problem.
- **Keep module loggers alive.** When configuring logging via `dictConfig`,
  set `disable_existing_loggers` to false so loggers created at import time
  are not silenced.

##### Never write runtime data into the application directory

- **The app directory may be read-only at runtime.** Don't create or write
  mutable files - a database, cache, uploads, or file logs - inside it;
  doing so fails when the filesystem is read-only (for example, SQLite then
  reports "unable to open database file").
- **Put writable state somewhere guaranteed writable and configurable.**
  Resolve the path from an environment variable, defaulting to a system temp
  directory, and use a mounted persistent volume when the data must survive
  restarts.
- **Keep read-only assets in the app directory.** Bundled lookup tables,
  templates, and static files belong there; writable state does not.

## Project

Project-specific guidance. The "### Overview" below is mandatory and written for
humans. Add detail inside it, and append any further sections (commands, stack,
structure, conventions, current state, …) after it.

### Overview

<!-- Required. In plain language a human can follow: What is this project? What
     does it do, and for whom? Replace this comment with that description. -->
