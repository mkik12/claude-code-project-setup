---
description: Save the session and end it.
---

End the current assistant session:

1. Update CLAUDE.md's "## Overview" so it still reflects what the app is and the
   technologies it uses; keep it concise, not a changelog. Keep the "## Project
   status" block accurate.
2. Update `.claude/session-memory.md`: add what this session did as a short
   entry, and compress older entries so the file stays small (recent sessions in
   detail, older ones a line each).
3. If significant work is uncommitted, commit it per the commit owner chosen at
   `/initialize`: if the user commits, tell them what to commit; otherwise commit
   yourself with a short message (`Co-authored-by: Claude` is fine).
4. Say goodbye and tell the user they can close this session and start another
   later with `/start`.
