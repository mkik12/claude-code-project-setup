
# Project memory

<!--
  Claude writes this file. The user does not edit it by hand.

  It sits at the project root and not inside `.claude/`, because `.claude/` is a
  protected path: a write there asks for confirmation every time, and no
  settings entry turns that off. `.claude/CLAUDE.md` imports this file, so both
  sections load into every session. Keep the whole file under 100 lines.
-->

## About the project

<!--
  One or two paragraphs: what the application does, who uses it, and which
  external systems it needs. This section changes rarely.
-->

Nothing recorded yet. Claude fills this in during the first session.

## Decisions

<!--
  A journal, newest entry at the top. This is not a changelog: git holds what
  changed already. This section holds what git cannot. Why we chose this way,
  what we rejected, what is half-finished, and which trap somebody hit.

  One entry:

      ### 2026-03-14 - Read the exposure view at request time

      A startup connection to LDWH1 crash-looped the pod before `/health`
      answered, so the connection moved into the request path.
      Rejected: a retry loop at startup, because it hides a dead warehouse.

  At 100 lines, compress the oldest entry into one dated line.
-->

Nothing recorded yet. Claude adds the first entry after the first piece of work.
