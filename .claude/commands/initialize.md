---
description: Interview the user and set up a new project (run once).
---

Initialize this project. You are the main session and the only thing that talks
to the user; delegate planning and coding to the `planner` and `coder`
subagents.

1. Ask the intake questions from `.claude/project-intake.md`, one at a time, in
   plain language, and record each answer back into that file. Read any input
   materials the user provides.
2. Choose scaffolding and architecture - the planner proposes, the user confirms
   (yes/no), and you re-plan on "no":
   - on CodeNow: propose which CodeNow component to create the repository from,
     then propose the architecture template (Flask, FastAPI, or Dash).
   - otherwise: propose the architecture template only.
3. Ask for a repository link and wait for it:
   - CodeNow: tell the user to create the repo in CodeNow from the chosen
     component and paste the link.
   - otherwise: ask for a link to an (empty) git repository.
   Bring the repo into the working directory - the same folder as `.claude/`. A
   plain `git clone` refuses a non-empty directory, so instead run `git init`,
   `git remote add origin <link>`, `git fetch origin`, then check out the default
   branch (e.g. `git checkout main`). The app is built here, next to `.claude/`.
4. Fill in CLAUDE.md's "## Project status" block: set **Initialized** to `yes`,
   and record the template, whether it publishes to CodeNow, the repository link,
   and who commits. Write the project overview into the "## Overview" section.
5. Update `.claude/session-memory.md` with a short note of what was set up.

Then flow straight into the first work round: delegate to the `planner` and
`coder` to build the initial app structure (the folder layout and a running
skeleton), verify it, and report what was built.
