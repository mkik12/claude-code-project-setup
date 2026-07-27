---
description: Save the session and end it.
---

End the current assistant session:

1. Stop any running app instance (as `/kill` does), so nothing is left running
   after the session.
2. Update CLAUDE.md's "## Overview" so it still reflects what the app is and the
   technologies it uses; keep it concise, not a changelog. Keep the "## Project
   status" block accurate, and keep `README.md` current (overview, how to run,
   and external resources).
3. Update `session-memory.md`: add what this session did as a short
   entry, and compress older entries so the file stays small (recent sessions in
   detail, older ones a line each).
4. If significant work is uncommitted, commit and push it per the commit owner
   chosen at `/start`: if the user owns commits, tell them what to commit and
   push; otherwise commit yourself with a short message (`Co-authored-by: Claude`
   is fine) and push. Do not end the session leaving commits unpushed.
5. Say goodbye and tell the user they can close this session and start another
   later with `/start`.
