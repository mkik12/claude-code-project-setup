---
description: 'Run the app locally in the background and show the user how to open and test it.'
---

Run the project's app so the user can see and try it. You are the main session
and the only thing that talks to the user.

1. Check the **Initialized** field in `PROJECT.md`'s "## Project status". If it is
   `no`, tell the user to run `/start` first to set the project up, then stop.
2. Start the Flask app locally through the Flask CLI, run from the project
   virtual environment (venv) by its exact relative interpreter path, in the
   background so this session stays usable, and capture the URL it prints on
   startup (e.g. `http://127.0.0.1:8080`):

   `.venv/Scripts/python.exe -m flask --app src.app run --port 8080 --debug`

   Keep it to that one command - no `cd`, no chaining - so it matches the
   allowed list and does not prompt.

   `--debug` belongs here and never in `app.py`: it gives you the auto-reloader
   and template reloading, so most edits need only a browser refresh rather than
   a restart, while the file that ships to CodeNow carries no debug flag. See
   the "Conventions" section of `.github/instructions/flask.instructions.md`.

   If that output says the port is already in use, an instance is already
   running and yours did not start. Do not start another, and do not let step 3
   mislead you - the old instance answers, so the check passes and a failed
   start reads as a success. Treat a stop-and-respawn as a fallback for what the
   auto-reloader does not cover - for example a changed config file it does not
   watch, or a reload that silently failed - rather than the routine response to
   every edit: stop it as `/kill` does and spawn once more only if you suspect
   that; otherwise keep it and tell them it was already running.
3. Verify it is up before handing over a link: request that URL (on CodeNow,
   confirm `/health` returns `{"status":"UP"}`). If it does not start or respond,
   do not give the user a broken link - report the failure, and if it is a code
   problem hand it to the `coder` to fix.
4. Tell the user, in their language: the URL to open, what they should see, how to
   try the main feature, and that `/kill` stops the app when they are done. That
   is four things, so lay it out as separate blocks or bullets rather than one
   paragraph - see **Make it easy to read** in `copilot-instructions.md`.
