---
description: Start an assistant session; on first run, set the project up.
---

You are the main session and the only thing that talks to the user; delegate
real work to the `planner` and `coder` subagents.

1. Read `CLAUDE.md` and `session-memory.md` (if it exists).
2. Greet the user, and in the greeting mention once that if they would rather not
   answer permission prompts, they can set their mode to Auto (the mode selector
   below the input box, or Shift+Tab); if Auto is not offered, they just keep
   approving prompts as normal.
3. Check the **Initialized** field in CLAUDE.md's "## Project status" block:
   - If `yes`: give a one-line summary of where the project stands (from session
     memory), then wait for the user's input - do not start any coding here.
   - If `no`: briefly explain what this assistant does (builds Python web apps
     through a plan-and-code workflow), then set the project up now by carrying
     out the setup steps below. Do not wait for another command.

## Setup (first run only)

1. Ask the intake questions from `project-intake.md`, one at a time, in plain
   language, and record each answer back into that file. Read any input materials
   the user provides.
2. This folder is already a clone of the project's CodeNow repository in
   Bitbucket: the assistant framework and the scaffold ship together in the
   CodeNow component, so a repo created from it arrives with both. There is
   nothing to connect and no link to ask the user for. Read the repository URL
   with `git remote get-url origin` and use it in the next step. If there is no
   `origin` remote, the folder was not cloned from CodeNow - say so and stop
   rather than running `git init`.
3. Fill in CLAUDE.md's "## Project status" block: set **Initialized** to `yes`,
   and record the language, the repository link, and who commits. Write the
   project overview into the "## Overview" section.
4. Update `session-memory.md` with a short note of what was set up.
5. Then flow straight into the first work round: delegate to the `planner` and
   `coder` to build the initial app structure (the folder layout and a running
   skeleton), verify it, and report what was built.
6. Write `README.md` (replacing the placeholder): the application name, the owner
   (the developer setting up the project - from `git config user.name`, or ask),
   a short overview (the detail lives in the app's external docs), how to run it,
   and the external resources it needs.
