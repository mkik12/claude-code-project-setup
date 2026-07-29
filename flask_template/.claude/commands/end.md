---
description: Save the session and end it.
---

End the current assistant session:

1. Stop any running app instance (as `/kill` does), so nothing is left running
   after the session.
2. Update `PROJECT.md`'s "## Overview" so it still reflects what the app is and the
   technologies it uses; keep it concise, not a changelog. Keep the "## Project
   status" block accurate, and keep `README.md` current (overview, how to run,
   and external resources).
3. Update `session-memory.md`: add what this session did as a short entry, then
   compress older ones so the whole file stays **under 100 lines** - recent
   sessions in a few lines each, older ones collapsed to one. It is loaded into
   every session, so this is the only thing stopping it growing without bound.
   If you already wrote an entry for this conversation, revise that one instead
   of adding a second: one conversation is one entry, however many times `/end`
   runs. The rest of the steps here can safely repeat; this one cannot.
4. Before committing anything, run the tests and pylint once. This is the last
   point before the code reaches the repository, where CI runs them anyway, so a
   failure found here costs a minute and a failure found there costs a pipeline.
   - If they pass, say so in one line and continue.
   - If anything fails, **do not commit it silently.** Report what failed and ask
     whether to fix it now or commit as-is - work is sometimes deliberately left
     mid-flight, and that is the user's call, not yours.
5. If significant work is uncommitted, commit and push it per the commit owner in
   `PROJECT.local.md`: if the user owns commits, tell them what to commit and
   push; otherwise commit yourself with a short message (`Co-authored-by: Claude`
   is fine) and push. Do not end the session leaving commits unpushed.
6. Say goodbye and tell the user they can close this session and start another
   later with `/start`.
