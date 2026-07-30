---
description: 'Stop the locally running app and all of its instances.'
---

Stop the app started by `/spawn`. You are the main session. Keep this minimal:
process-management commands like these are the ones most likely to need an
explicit approval, so run as few as possible - every extra command is another
prompt for the user.

1. The app's port is 8080 - the scaffold's `app.run` port. This command only
   ever stops a local run, so ignore the CodeNow port in `.codenow.yaml`.
2. On Windows, run this through **PowerShell, not Git Bash / WSL**: find the
   listener PIDs with `netstat -ano`, then stop each one with
   `taskkill /F /PID <pid>`. A POSIX shell can rewrite `/F` into a path and make
   the command fail with "Invalid argument/option" while the app keeps running -
   see `4_things_to_look_out.md` in the framework repo for the reproduction. On
   macOS/Linux use `lsof -ti tcp:8080` and then `kill`. Stop every listener so no
   instance is left running.
3. `/spawn` runs the app with `--debug`, so the reloader holds two processes and
   the child keeps the socket when the parent dies. If `taskkill` reports a PID
   as not found while the port still answers, that surviving child is why, and
   `netstat` may keep naming the dead parent. Stop the `python` processes by
   their command line instead. This is the one case worth the extra prompt.
4. Do not pad this out otherwise: no piped one-liners, no repeated re-checks,
   and no process listing unless step 3 applies. Run at most one final check
   that the port is free. If nothing was listening, say so - that is not an
   error.
