---
description: Stop the locally running app and all of its instances.
---

Stop the app started by `/spawn`. You are the main session. Keep this minimal:
the process tools below are deliberately not allow-listed, so each one prompts.
Every extra command is another prompt for the user - run as few as possible.

1. The app's port is 8080 - the scaffold's `app.run` port. This command only
   ever stops a local run, so ignore the CodeNow port in `.codenow.yaml`.
2. On Windows, run this through the **PowerShell tool, not Bash**: find the
   listener PIDs with `netstat -ano`, then stop each one with
   `taskkill /F /PID <pid>`. Through a POSIX shell the flags get rewritten into
   paths - `/F` becomes `F:/` - so the command fails with "Invalid
   argument/option" and the app keeps running. On macOS/Linux use
   `lsof -ti tcp:8080` and then `kill`. Stop every listener so no instance is
   left running.
3. Do not pad this out: no `Get-CimInstance`, no piped one-liners, and no
   repeated re-checks. Run at most one final check that the port is free. If
   nothing was listening, say so - that is not an error.
