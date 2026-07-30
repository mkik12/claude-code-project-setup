
# GitHub Copilot implementation

How the design in `2_workflow.md` is realized in GitHub Copilot (VS Code). Read
that document first; this one only covers the Copilot-specific mechanics.

**Status: built, not yet verified in a live session.** Every file below exists in
`flask_template/.github/` and mirrors its Claude Code counterpart in `.claude/`
line for line where the design is identical, and only diverges where VS Code's
mechanics genuinely require it. Nothing here has been run end to end yet - see
"Still to verify" at the end before treating this as equivalent-in-practice to
the Claude Code side.

## Layout

A project created from the component contains, alongside the `.claude/` layout
`3a_claude_workflow.md` describes:

~~~
PROJECT.md             project status and overview, committed and shared
PROJECT.local.md       this person's language and commit owner, gitignored
session-memory.md      rolling cross-session summary, written at runtime
pytest.ini             sets the test import path, once
tests/
  conftest.py           the `client` fixture wrapping Flask's test client
  test_app.py           smoke tests guarding the CodeNow contract
.github/
  copilot-instructions.md   how Copilot works here, never written at runtime
  intake.md                 the read-only interview script
  agents/
    planner.agent.md
    coder.agent.md
  prompts/
    start.prompt.md  spawn.prompt.md  kill.prompt.md  end.prompt.md
  instructions/
    code-style.instructions.md  flask.instructions.md  codenow.instructions.md
~~~

Unlike `.claude/`, `.github/` is not a protected path in VS Code - there is no
Copilot-specific reason the writable project files (`PROJECT.md`,
`session-memory.md`) could not live inside it. They stay at the project root
anyway, because that layout is shared: both assistants read the same files, and
a project has to work whichever one is active.

## copilot-instructions.md and PROJECT.md

The same split as Claude Code: **`copilot-instructions.md` is Copilot's
instructions, `PROJECT.md` is the project's state.** VS Code automatically
detects `.github/copilot-instructions.md` in the workspace root and applies it to
every chat request.

One real difference from `CLAUDE.md`: **there is no import mechanism.**
`CLAUDE.md` pulls `PROJECT.md` and `session-memory.md` into context at launch with
`@../PROJECT.md`; nothing in `copilot-instructions.md` can do that. So, unlike the
Claude side - where `4_things_to_look_out.md` warns against ever telling the
assistant to read an already-imported file - `copilot-instructions.md` **does**
instruct reading both files, once, at the start of a session. That instruction is
correct here specifically because the import does not exist; do not "fix" it by
copying Claude's wording.

`copilot-instructions.md` holds only how this assistant works: the subagents, the
commands, the rules index, the philosophy, and the working rules. It is identical
across every project, must not be edited per-project, and is never written at
runtime - same contract as `CLAUDE.md`.

## Subagents

`.github/agents/planner.agent.md` and `.github/agents/coder.agent.md`. Each is a
markdown file whose frontmatter sets `name`, `description`, and `model`.

**This is where the Copilot side deliberately diverges from Claude Code**, which
has both subagents inherit the session's model. Copilot bills per token, the
models differ enough in rate to matter, and each role has a different shape:
the planner is reasoning-bound on short output, the coder is output-heavy and
loops. So the models are pinned per role:

| Agent | `model` |
| :--- | :--- |
| `planner` | `['GPT-5.6 Luna (copilot)', 'GPT-5.4 mini (copilot)']` |
| `coder` | `['MAI-Code-1-Flash (copilot)', 'GPT-5.4 mini (copilot)']` |

Three things make this fragile enough to write down:

- **A subagent may not exceed the main session's cost tier.** If it tries, it
  silently falls back to the main model. The main session's model is the VS Code
  picker selection and **no file in the repository can set it**, so `/start`'s
  greeting asks the user to set it to GPT-5.6 Luna. Leave the picker on
  something cheaper and both subagents quietly run on that instead.
- **The array is an availability fallback, not a quality one.** VS Code tries
  each entry in order until one is available. It does not advance because a
  model is performing badly, and it does not rescue a cost-tier violation -
  that resolves to the main model regardless of what else is listed.
- **IDs are picker display names with a `(copilot)` suffix**, not kebab-case API
  ids. An unresolvable name fails silently by falling back, and the hover
  tooltip shows the parent model either way, so verify by the per-subagent AI
  credits readout rather than by the label.

The rates and the reasoning behind the choice are in
`copilot_model_audit_RESULT.md`. Re-check it if the promotional pricing on
Claude Sonnet 5 lapses or the roster changes, since both move the arithmetic.

- `planner` sets `tools: ['search', 'usages']` and `user-invocable: false`. The
  tool list is read-only by construction, and hiding it from the agent picker
  keeps it reachable only as a subagent, matching "proposes, does not implement"
  being structural rather than merely instructed. The exact toolset names
  available may shift between VS Code versions - check the Tools picker against
  this list the first time a project actually runs `/start`, and the body also
  says explicitly never to edit or run commands even if a broader tool becomes
  available, as a second line of defense.
- `coder` sets no `tools` line and so inherits the full set, and also sets
  `user-invocable: false` for the same reason as `planner`.
- The `description` is what the active session matches on when deciding to
  delegate, same role as in Claude Code's agent files.

Delegation itself relies on VS Code's subagent invocation for custom agents: an
agent can call another custom agent and get back a single report, which is the
mechanic this whole design needs. As of this writing VS Code's own documentation
marks running a custom agent as a subagent **experimental**. `copilot-instructions.md`
says so and gives a fallback: if delegation is unavailable, do the planning and
coding directly in the main session, in that order, rather than silently skipping
one.

## Commands

`.github/prompts/*.prompt.md` become the slash commands `/start`, `/spawn`,
`/kill`, and `/end`, the same role as `.claude/commands/*.md`. The frontmatter
carries a one-line `description`; the body is the instruction the main session
follows. None sets an `agent:` field, so each runs in whatever agent is currently
active rather than switching into `planner` or `coder` - the main session is the
default agent, not a custom agent of its own, exactly as in Claude Code.

`/start` doubles as first-run setup, for the same reason as the Claude version:
there is no separate `/initialize`.

## Rules

`.github/instructions/*.instructions.md` holds the same three files as
`.claude/rules/`: `code-style.instructions.md`, `flask.instructions.md`, and
`codenow.instructions.md`. Their content is identical to the Claude versions -
none of it is Claude-specific - only the frontmatter changed.

That frontmatter change is not cosmetic. Claude Code's rule files load at launch
unless they carry `paths` frontmatter to scope them; Copilot's instructions files
do the opposite by default - **an instructions file with no `applyTo` is never
applied automatically.** So where the Claude side left `paths` off deliberately to
get always-on loading, the Copilot side has to set `applyTo: '**'` explicitly to
get the same result. Leaving it off here would silently turn every rule
conditional, which is the one place a literal file-for-file copy would have
quietly broken the design.

## What has no Copilot equivalent

Claude Code's `.claude/settings.json` allow/deny list has no shippable
counterpart in `.github/`. The nearest mechanism, `chat.tools.terminal.autoApprove`,
is a different kind of setting - regex-based command approval configured in
`.vscode/settings.json`, a VS Code editor setting rather than a version-controlled
agent-customization file - and this framework does not ship one. State this gap
plainly rather than filling it with something that only looks equivalent: a user
who wants fewer prompts configures VS Code's permission level or terminal
auto-approval themselves, the same way Claude Code users opt into Auto mode
themselves rather than a template granting it.

The consequence for the agents: `copilot-instructions.md` keeps the "no `cd`
prefixes, no `&&` chains" rule from Claude Code, because VS Code's terminal
auto-approval also fails a compound command if any one link is unmatched - the
same reasoning, not a copied assumption.

## Still to verify

Nothing below is guessable from documentation; each needs a real session:

- Whether `planner` and `coder` actually run in isolation when invoked from the
  main session's copilot-instructions.md, and whether their reports land in the
  main session without being shown to the user as raw chat turns.
- Whether `.claude/` and `.github/` coexisting in the same project causes VS Code
  to load both sets of agents/instructions at once for a Copilot session (VS Code
  is documented to detect `.claude/agents` directly). If so, decide whether that
  is harmless duplication or something to suppress.
- The exact tool/toolset names available to `planner` - confirm `['search',
  'usages']` actually excludes edit and terminal tools in the live Tools picker.
- Whether `chat.instructionsFilesLocations`/`chat.agentFilesLocations` defaults
  need any project-level configuration, or whether `.github/instructions` and
  `.github/agents` are searched out of the box (expected, per VS Code's default
  locations, but not yet confirmed against a real project).
