
# Claude Code implementation

How the design in `2_workflow.md` is realized in Claude Code. Read that document
first; this one only covers the Claude-specific mechanics. The behaviour that
motivated several of the choices below is documented in
`4_things_to_look_out.md`.

## Layout

A project created from the component contains:

~~~
PROJECT.md             project status and overview, committed and shared
PROJECT.local.md       this person's language and commit owner, gitignored
session-memory.md      rolling cross-session summary, written at runtime
pytest.ini             sets the test import path, once
tests/
  conftest.py          the `client` fixture wrapping Flask's test client
  test_app.py          smoke tests guarding the CodeNow contract
.claude/
  CLAUDE.md            how Claude Code works here, never written at runtime
  intake.md            the read-only interview script
  settings.json        permissions
  agents/
    planner.md
    coder.md
  commands/
    start.md  spawn.md  kill.md  end.md
  rules/
    code-style.md  flask.md  codenow.md
~~~

The division is by **what gets written at runtime, not by what the file is
about**. `.claude/` is a protected path: writes there prompt in every mode and
cannot be allow-listed, because the safety check runs before Claude Code
evaluates allow rules. So everything the assistant rewrites during a session
sits at the project root, where it falls under `acceptEdits`, and everything
static lives in `.claude/`.

`CLAUDE.md` is static, so it belongs in `.claude/` with the rest of the config.
That is only true because `PROJECT.md` exists to absorb the parts that change.

## CLAUDE.md and PROJECT.md

The split matters: **`CLAUDE.md` is Claude's instructions, `PROJECT.md` is the
project's state.** Claude Code reads a project instruction file from either
`./CLAUDE.md` or `./.claude/CLAUDE.md`; this template uses the latter. It opens
with two imports, `@../PROJECT.md` and `@../session-memory.md`, so the project
state and the session history land in context at launch without a single tool
call. The `../` is required: import paths resolve relative to the file containing
them, so a bare `@PROJECT.md` would look for `.claude/PROJECT.md` and find
nothing.

Because they are imported, no command should ever instruct the assistant to read
them. `/start` says so explicitly, since the instruction it replaced ("read
`PROJECT.md` and `session-memory.md`, if it exists") produced three wasted calls
per session: two redundant reads and a Glob triggered by the hedge.

`CLAUDE.md` holds only how this assistant works: the subagents, the commands,
the rules index, the philosophy, and the working rules. It is identical across
every project, must not be edited per-project, and is never written at runtime.

`PROJECT.md` holds what changes and is shared:

- **`## Project status`** - `Initialized` and `Repository`. The `Initialized` field
  is one of the two gates `/start` branches on.
- **`## Overview`** - what the project is, in plain language.

`PROJECT.local.md` holds what is personal: the language to speak and whether the
user or the assistant commits. It is gitignored, so each person on a shared
project has their own, and it is deliberately **not** imported - a gitignored file
does not exist in a fresh clone, so an import would point at nothing on a
colleague's first session. `/start` reads it instead, and its absence is the second
gate: no local file means someone new to an existing project, who gets asked only
those two questions.

Keeping them apart buys two things. `PROJECT.md` belongs to the project rather
than to Claude, so a second assistant reads the same status instead of keeping a
private copy that drifts. And because nothing writes to `CLAUDE.md` any more, it
is static config, which is what lets it live in the protected `.claude/`
directory at no cost.

Target under 200 lines each. Detailed conventions live in `.claude/rules/`, which
Claude Code also loads at launch, so the always-on context is both files plus all
three rules - about 360 lines. That is a deliberate choice: the rules apply to
most work, and scoping them with `paths` frontmatter to save a couple of hundred
lines is not worth the risk of the relevant one failing to load.

## Subagents

`.claude/agents/planner.md` and `.claude/agents/coder.md`. Each is a markdown
file whose frontmatter sets `name`, `description`, and `model`.

- Both set `model: inherit`, so they run on whatever model the user chose for the
  session. Never hardcode a model.
- `planner` is restricted to `tools: Read, Grep, Glob`. It cannot write or run
  anything, which is what keeps "proposes, does not implement" structural rather
  than merely instructed.
- `coder` has no `tools` line and so inherits the full set.
- The `description` is what the main session matches on when deciding to
  delegate, so it states when to use the agent, not just what it is.

Each agent file names the rule files to read before starting, since subagents do
not inherit the main session's loaded context.

## Commands

`.claude/commands/*.md` become the slash commands `/start`, `/spawn`, `/kill`,
and `/end`. The frontmatter carries a one-line `description`; the body is the
instruction the main session follows.

`/start` doubles as first-run setup. There is no separate `/initialize`: the
command checks its two gates and either reports status, sets up just this person,
or runs the full setup, all in the same session.

## Rules

`.claude/rules/` holds the detail that would otherwise bloat CLAUDE.md:

- `code-style.md` - engineering principles and formatting for Python, HTML, CSS,
  and JavaScript, plus the `.gitignore` pattern list.
- `flask.md` - the app structure and conventions for this template. One file per
  architecture; a FastAPI or Dash template swaps this file.
- `codenow.md` - what the component provides, the platform contract that must
  keep working, the logging rules, and the read-only-app-directory rule.

CLAUDE.md indexes them and says to read the relevant one before the work that
needs it.

## Permissions

`.claude/settings.json` sets `defaultMode: "acceptEdits"` and ships a
conservative allow-list so the assistant can run the framework's own tools (git,
Python, pip, pytest, pylint, flask, waitress) without a prompt.

Every rule is written twice, once for `Bash(...)` and once for `PowerShell(...)`.
They are separate tools with separate rule namespaces, and PowerShell is the
primary shell on Windows, so a Bash-only list would still prompt for everything.

Three things shape how Claude Code applies the file:

- **Allow rules need workspace trust.** Claude Code applies a project's
  `permissions.allow` rules only after the user accepts the one-time "trust this
  folder" dialog for that workspace; until then the rules are read but ignored.
  Deny rules are never loosened by trust, since they only restrict.
- **Deny rules match a command prefix, not a parsed command line.** A wildcard
  can sit anywhere in the pattern, so the force-push denials are written
  `git push *--force*` (and the `-f` forms) rather than `git push --force*`,
  which a reordered `git push origin main --force` would slip past.
- **`auto` mode cannot be shipped in the template.** Claude Code ignores
  `defaultMode: "auto"` in project and local settings by design, so a repository
  cannot grant itself auto mode, and it is eligibility-gated besides. Users opt
  in through their own `~/.claude/settings.json` or the in-session mode toggle,
  which is why `/start` mentions it once in the greeting.

The deny list covers force-push and `rm -rf`, plus `git clean` and
`git reset --hard`. The allow-list needs a broad `git *` rule to keep commits and
pushes prompt-free, and those two commands destroy uncommitted work as
irreversibly as `rm -rf` does.

Networking and process commands the app-run flow uses (curl, netstat, taskkill)
are intentionally left to prompt; users who want them silent can enable `auto`
mode or allow them locally. `/kill` is written to run as few of them as possible
for that reason.

## Consequences for how the agents work

Two rules in CLAUDE.md exist purely because of the permission model, and look
arbitrary without it:

- **no `cd` prefixes and no `&&` chains.** Claude Code splits a compound command
  on shell operators and requires every subcommand to match a rule
  independently, so one unmatched link prompts for the whole chain.
- **set the test import path once** in `conftest.py` rather than prefixing
  `PYTHONPATH=...` onto every pytest invocation, for the same reason.

The coder also invokes the venv interpreter by its exact relative path
(`.venv/Scripts/python.exe` or `.venv/bin/python`), with no quotes and no
absolute prefix, so the command matches the allow-list as written.
