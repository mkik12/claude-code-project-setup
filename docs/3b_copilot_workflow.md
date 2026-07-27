
# GitHub Copilot implementation

**Status: not built.** This document scopes the work rather than describing
something that exists. In the template, `.github/` currently holds only a
`.gitkeep` placeholder.

Read `2_workflow.md` for the design this has to implement, and
`3a_claude_workflow.md` for the Claude Code version to mirror.

Nothing below has been verified against current Copilot behaviour. The feature
names are the expected mapping and must be confirmed against GitHub's
documentation before anything is written, because this is exactly the kind of
detail that changes between releases.

## What needs an equivalent

| Design element (`2_workflow.md`) | Claude Code            | Copilot candidate                 |
| :------------------------------- | :--------------------- | :-------------------------------- |
| Operating file, always loaded    | `CLAUDE.md`            | `.github/copilot-instructions.md` |
| Rules read on demand             | `.claude/rules/*.md`   | `.github/instructions/*.instructions.md` (`applyTo` frontmatter) |
| planner and coder subagents      | `.claude/agents/*.md`  | `.github/chatmodes/*.chatmode.md` |
| start / spawn / kill / end       | `.claude/commands/*.md`| `.github/prompts/*.prompt.md`     |
| Permission allow-list            | `.claude/settings.json`| no direct equivalent - see below  |

## Open questions

These need answering before the mapping above is worth implementing:

- **Delegation.** The design depends on a main session that delegates to two
  isolated subagents and reads back a single report. If Copilot chat modes
  cannot be invoked programmatically by another mode, the planner/coder split
  has to be reworked into something a single session drives, and `2
  workflow.md`'s role model stops being shared between the two assistants.
- **Isolation.** Subagents in this framework return one report and keep nothing.
  Whether a Copilot chat mode gives equivalent context isolation is unknown.
- **Permissions.** Copilot has no counterpart to `settings.json` allow and deny
  rules. The safety properties the Claude version gets from denying force-push,
  `rm -rf`, `git clean`, and `git reset --hard` would have to come from
  somewhere else, or be accepted as absent and stated plainly.
- **The writable-files decision.** The three operating files sit at the project
  root because `.claude/` is protected. That reason is Claude-specific, so
  Copilot may have no need for the same layout - but the layout is shared,
  because both assistants read the same repository. Keep the root layout and
  document why, rather than splitting it.
- **Both at once.** A project created from the component will contain `.claude/`
  and `.github/` together. Decide whether the two are expected to be used
  interchangeably on the same repository, and if so, which one owns
  `session-memory.md` and `project-intake.md` so they do not fight over them.

## Constraint

Whatever is built here writes into the same repository the Claude version does.
`session-memory.md`, `project-intake.md`, and the project status block are shared
state with a shared format. Diverging on their structure would mean a project
could not switch assistants, so treat the format defined in `2_workflow.md` as
fixed and adapt around it.
