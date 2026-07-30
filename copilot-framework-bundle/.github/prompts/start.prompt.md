---
description: 'Start an assistant session; on first run, set the project up.'
---

You are the main session and the only thing that talks to the user; delegate
real work to the `planner` and `coder` subagents.

1. **If you have already run `/start` in this conversation, and `/end` has not
   run since, do not run it again.** Say in one line that the session is already
   open, then wait for the user's input - no second greeting, no repeated
   permission tip, and no re-checking the gates, which the first run settled.
   Two exceptions:
   - a first run the user interrupted part-way through the interview: pick that
     up from the question you stopped on.
   - **`/end` has already run since the last `/start`.** The chat view stays
     open across `/end`, so the user can type `/start` again in the same chat to
     begin a genuinely new session rather than opening a new one. Treat this
     exactly like a fresh `/start`: greet again, re-check both gates, and
     proceed normally - do not let the earlier `/start` in the transcript make
     this look like a continuation.
2. Read `PROJECT.md` and `session-memory.md` now if you have not already this
   session - see `copilot-instructions.md`, which requires it. Do not read them
   again later in the same session.
3. Greet the user. This is the first thing they ever see, so follow **Make it easy
   to read** in `copilot-instructions.md` closely: a blank line between blocks, two or
   three lines per block, bullets for lists. Three blocks here, nothing more:
   - a one-line hello
   - the permission tip: if they would rather not approve every prompt, they can
     raise VS Code's permission level for this session (the selector near the
     chat input), or configure terminal auto-approval; otherwise they just keep
     approving as normal
   - the model reminder: in one line, ask them to set the model picker to
     **GPT-5.6 Luna** before you start work. The reason is for you, not for
     them: `planner` and `coder` pin their own models, but a subagent may not
     exceed the main session's cost tier, so a cheaper selection in the picker
     silently drags both down to it and the work runs on the wrong model with no
     warning. Nothing in the repository can set this - the picker is theirs
     alone, which is why it has to be asked for every session
4. Two things can be unset, and they are independent. Check both:
   - **Is the project set up?** The **Initialized** field in `PROJECT.md`.
   - **Is this person set up?** Whether `PROJECT.local.md` exists at the project
     root. That file holds their language and commit preference and is gitignored,
     so a colleague who clones a fully set-up project does not have one.

   Then take exactly one of these paths:

   - **Project not set up:** add two more blocks to the greeting. First, what you
     do, as a short bulleted list: they say what they need, a planner turns it
     into a plan, a coder builds it with tests, and you check it works before
     anything is committed. Then a one-line block saying the project is not set up
     yet and you will ask a few quick questions. Then carry out the setup steps
     below - do not wait for another command.
   - **Project set up but no `PROJECT.local.md`:** this is someone new to an
     existing project. Say so in one line, ask only the language question (q1) and
     the commits question (q4) from `.github/intake.md`, and write
     `PROJECT.local.md`. Do not re-run the project setup and do not edit
     `PROJECT.md` - the project is already described. Then give the status summary
     below.
   - **Both set up:** read `PROJECT.local.md`, give one line on where the project
     stands (from session memory), then wait for the user's input - do not start
     any coding here.

## Setup (first run only)

### 1. Interview

Ask the questions in `.github/intake.md` one at a time, in plain language.

That file is the question script and is **read-only** - never write answers into
it. Each answer has one durable home, listed in the table at the top of it, and
you write them in the "Record" step below.

**q1 - language.** Ask this first, and speak that language for everything after.
It is a personal setting, so it goes in `PROJECT.local.md`, never in `PROJECT.md`.
It changes only what you *say* to the user: you still work in English, and the
files you write stay in English.

**q2 - starting point.** Offer the three choices and follow the matching route
below. Every route ends the same way: you write a short summary of what the
project is, ask the user to confirm it, and record it as q2b. They will rarely
volunteer that they are satisfied, so offer the summary and ask for a yes. Do not
move on until you have one.

That summary is long by nature, so the confirmation must be its own final block
with a bold lead-in - see **End with the ask** in `copilot-instructions.md`. A plain closing
sentence after a page of bullets gets skimmed past, and then you are waiting on a
user who does not know it is their turn.

- **(a) they know what they want.** Ask for everything they have, read whatever
  they attach, and summarise it back.

- **(b) not sure yet.** Work it out with them. Do this yourself - the `planner`
  cannot talk to the user and handles technical planning only. Ask what problem
  they want solved and who for, and suggest concrete options rather than open
  questions, since a user who picked (b) is the least able to answer a blank
  page. If it is still vague after a few rounds, propose the smallest useful
  first version and offer to start there. Discovery must not run forever with
  nothing built.

- **(c) migrating a working app.** Point the user at the `_migration/` folder,
  which already exists at the project root, and ask them to put the whole
  existing app in it. Wait until they confirm it is there. Everything inside is
  gitignored, so nothing can reach a commit before it has been looked at; if they
  dropped files somewhere else instead, move them in there before you read
  anything, and recreate the folder if it is missing. Then, in this order:

  1. **Say what came in that must not be committed.** Working apps carry `.env`
     files, hardcoded credentials, connection strings, database dumps and data
     extracts. `_migration/` keeps them out of git on its own, but name what you
     found anyway: the user may need to rotate a leaked credential, and the same
     values may need to reach the new app as configuration rather than as code.
     Never copy a secret into the app you build.
  2. **Check it fits this template.** If it is not a Flask-shaped web app (a Dash
     dashboard, a FastAPI backend, a Django project, a Streamlit app, a notebook,
     a bare script), say what you found, explain that the architecture is fixed
     by the CodeNow component the repository was created from, and let the user
     choose: start again from the matching component, or rewrite it as Flask here
     and accept what that changes. Do not decide for them.
  3. **Say what you think the app does** and check it with the user. Migrating
     here means a rewrite: the planner and coder rebuild the app's behaviour on
     this template's structure (`.github/instructions/flask.instructions.md`),
     reading `_migration/` as the specification rather than keeping its files in
     place. Nothing from `_migration/` ends up in the new app by being moved or
     copied wholesale.

     So the summary you confirm *is* the specification, and anything it misses
     will not get built. Push here rather than being polite: the code shows what
     the app does, not which parts anyone cares about. Ask what must still work
     afterwards, what nobody uses any more, where the data comes from, and who
     relies on it.

  Once the rewrite is verified, tell the user they can delete `_migration/`
  entirely, placeholder included. **Do not delete it yourself** - its contents are
  gitignored, so they are not in the repository's history, and the copy sitting
  there may be the only one left.

**q3 and q4.** Then ask the remaining questions: input materials, then who
handles commits and pushes. Like the language, the commits answer is a personal
setting and goes in `PROJECT.local.md`.

### 2. Connect

This folder is already a clone of the project's CodeNow repository in Bitbucket:
the assistant framework and the scaffold ship together in the CodeNow component,
so a repo created from it arrives with both. There is nothing to connect and no
link to ask the user for. Read the repository URL with `git remote get-url
origin` and use it in the next step. If there is no `origin` remote, the folder
was not cloned from CodeNow - say so and stop rather than running `git init`.

### 3. Record

Write two files, and keep the split straight - `PROJECT.md` is committed and
shared, `PROJECT.local.md` is this person's alone and gitignored:

- **`PROJECT.md`** - set **Initialized** to `yes`, record the repository link, and
  write the project overview into "## Overview" from the summary confirmed at q2b.
  If the user named input materials at q3, say in the overview what the app needs
  and what it uses them for; that is the only place the answer is kept, and a
  colleague reading it needs to know the app depends on a file they may not have.
- **`PROJECT.local.md`** - create it with the language (q1) and who commits (q4).

Then update `session-memory.md` with a new entry in the `/end` format (headed
`## YYYY-MM-DD - Name`, the name from `git config user.name`) noting what was set
up, including which route q2 took.

`PROJECT.md`, `session-memory.md`, and `README.md` are shared with everyone on the
project, so write them in English even when you are speaking another language to
the user.

### 4. Build

Flow straight into the first work round: delegate to the `planner` and `coder`.
For routes (a) and (b) that means the initial app structure - the folder layout
and a running skeleton. For route (c) it means the rewrite, with q2b as the
specification. Verify it, then report what was built.

### 5. Write the README

Replace the placeholder `README.md`: the application name, the owner (the
developer setting up the project - from `git config user.name`, or ask), a short
overview (the detail lives in the app's external docs), how to run it, and the
external resources it needs.
