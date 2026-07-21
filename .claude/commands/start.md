---
description: Load the project context and start an assistant session.
---

You are starting an assistant session for this project. You are the main session
and the only thing that talks to the user; delegate real work to the `planner`
and `coder` subagents.

1. Read `CLAUDE.md` and `.claude/session-memory.md` (if it exists).
2. Check the **Initialized** field in CLAUDE.md's "## Project status" block.
   - If it is `no`: greet the user, briefly explain what this assistant does
     (builds Python web apps through a plan-and-code workflow), tell them to run
     `/initialize` to set the project up, then stop.
   - If it is `yes`: greet the user, give a one-line summary of where the project
     stands (from session memory), and wait for their input.

Do not start any coding in this command; just load context and hand back to the
user.
