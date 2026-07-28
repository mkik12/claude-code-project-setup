---
description: Run the app locally in the background and show the user how to open and test it.
---

Run the project's app so the user can see and try it. You are the main session
and the only thing that talks to the user.

1. Check the **Initialized** field in `PROJECT.md`'s "## Project status". If it is
   `no`, tell the user to run `/start` first to set the project up, then stop.
2. Start the Flask app locally with the built-in server (`app.run`, port 8080 -
   see the "Conventions" section of `.claude/rules/flask.md`). Run it from the
   project virtual environment (venv), in the background so this session stays
   usable, and capture the URL it prints on startup (e.g.
   `http://127.0.0.1:8080`).
3. Verify it is up before handing over a link: request that URL (on CodeNow,
   confirm `/health` returns `{"status":"UP"}`). If it does not start or respond,
   do not give the user a broken link - report the failure, and if it is a code
   problem hand it to the `coder` to fix.
4. Tell the user, in their language: the URL to open, what they should see, how to
   try the main feature, and that `/kill` stops the app when they are done. That
   is four things, so lay it out as separate blocks or bullets rather than one
   paragraph - see **Make it easy to read** in `CLAUDE.md`.
