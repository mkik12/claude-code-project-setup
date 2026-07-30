
# Things to look out for

Non-obvious behaviour that shaped how this framework is built. Each item fails
quietly rather than loudly, so it costs an afternoon to rediscover. Every claim
was checked against the Claude Code documentation or reproduced locally, and the
source is named so it can be re-checked when Claude Code changes.

## Claude Code permissions

### Bash and PowerShell are separate rule namespaces

`Bash(...)` and `PowerShell(...)` are two different tools with two different
sets of permission rules. A rule written for one does nothing for the other.

This matters most on Windows, where PowerShell is the primary shell. A
Bash-only allow-list looks complete and still prompts for every command. Every
rule in `settings.json` is therefore written twice.

Watch the details when mirroring: PowerShell canonicalizes aliases before
matching (a rule for `Get-ChildItem` also covers `gci`, `ls`, and `dir`), and
the path separator differs, so the venv interpreter needs both the
`.venv/Scripts/python.exe` and `.venv\Scripts\python.exe` spellings.

Source: [permissions - PowerShell](https://code.claude.com/docs/en/permissions).

### Allow rules do nothing until the workspace is trusted

> `permissions.allow` rules and `permissions.additionalDirectories` entries in a
> project's `.claude/settings.json` grant capability, so Claude Code applies
> them only after you accept the workspace trust dialog for that workspace.
> Until then, Claude Code reads the rules but doesn't apply them.

A project can ship a perfect allow-list and the first user still gets prompted
for everything until they accept the one-time dialog. `deny` and `ask` rules are
unaffected, because they only restrict.

Two wrinkles: trust is keyed on the git repository root, and trusting a parent
directory does **not** apply a nested project's allow rules.

Source: [permissions - project allow rules and workspace
trust](https://code.claude.com/docs/en/permissions).

### Protected paths cannot be allow-listed at all

`.claude/` is a protected path, alongside `.git`, `.config/git`, `.vscode`,
`.idea`, `.husky`, `.cargo`, `.devcontainer`, `.yarn`, and `.mvn`. In both
`default` and `acceptEdits` mode, writes there are prompted, and no settings
entry changes that:

> The safety check runs before Claude Code evaluates allow rules from settings,
> so an entry such as `Edit(.claude/**)` [...] does not change the per-mode
> outcome.

**This is the single reason the writable project files live at the project root
rather than in `.claude/`.** `PROJECT.md`, `session-memory.md`, and
`README.md` are rewritten during a normal session. Inside `.claude/`
every one of those writes would prompt, permanently and unfixably. At the root
they fall under `acceptEdits`. Only static config the assistant never edits at
runtime belongs in `.claude/`.

Note what this does *not* say: auto mode is not a way around it. Protected-path
writes in `auto` are routed to the classifier rather than auto-approved, so some
still stop, and a repository cannot enable auto mode for its users anyway. The
root layout works in every mode; a `.claude/` layout works only in `auto` and
`bypassPermissions`.

Source: [permission modes - protected
paths](https://code.claude.com/docs/en/permission-modes).

### A repository cannot grant itself `auto` mode

`auto` mode is the real prompt-killer, but it cannot be shipped in a template:

> Claude Code v2.1.142 and later ignore `auto` from those files so a repository
> cannot grant itself auto mode. Move it to `~/.claude/settings.json`.

It is also eligibility-gated by model and, on Team and Enterprise plans, by
organization policy. Setting `defaultMode: "auto"` in `.claude/settings.json`
fails silently: the session just starts in `default` with no error. This is why
`/start` mentions Auto in its greeting instead, leaving the user to opt in.

Source: [permission modes - eliminate prompts with auto
mode](https://code.claude.com/docs/en/permission-modes).

### Deny rules match a command prefix, not a parsed command line

Wildcards may sit anywhere in the pattern, and matching is textual. A rule
written `git push --force*` only catches the flag in first position, so

```
git push origin main --force
```

slips past it and is then approved by the broad `git *` allow rule. The denials
are written `git push *--force*` instead, with separate `-f` forms.

The same reasoning applies to `rm -rf` versus `rm -fr` versus `rm -r -f`. Treat
a deny rule as a safety net for realistic slips, not as a boundary against a
determined caller.

Source: [permissions - Bash](https://code.claude.com/docs/en/permissions).

### `acceptEdits` auto-approves destructive filesystem commands

`acceptEdits` is not limited to file edits:

> In addition to file edits, `acceptEdits` mode auto-approves common filesystem
> Bash commands: `mkdir`, `touch`, `rm`, `rmdir`, `mv`, `cp`, and `sed`.

With the PowerShell tool enabled it also auto-approves `Remove-Item`. The
template sets `defaultMode: "acceptEdits"`, so these run without asking for
paths inside the working directory. Deny rules still win, which is why the
destructive ones are denied explicitly rather than left to the mode.

The same argument covers `git clean` and `git reset --hard`. The allow-list
needs a broad `git *` rule to keep commits and pushes prompt-free, and those two
destroy uncommitted work as irreversibly as `rm -rf` does, so they are denied by
name.

Source: [permission modes -
acceptEdits](https://code.claude.com/docs/en/permission-modes).

### `.claude/rules/` files load at launch unless you scope them

A directory called `rules` reads as reference material fetched when needed. It is
not:

> Rules without `paths` frontmatter are loaded at launch with the same priority
> as `.claude/CLAUDE.md`.

So an instruction like "read the relevant rule before the work that needs it; do
not preload them" describes something that never happens - the files are already
in context. Worse, it implies the assistant is missing context it actually has.

To make a rule genuinely conditional, give it `paths` frontmatter:

```markdown
---
paths:
  - "src/**/*.py"
---
```

This framework deliberately leaves all three rules unscoped and accepts the
preloading. The always-on total is roughly 360 lines across `CLAUDE.md`,
`PROJECT.md`, and the rules, which is a modest share of the context window, and
the rules apply to most work anyway. Scoping them would trade that for the risk
of the relevant rule not loading when it matters.

### Shell operators split a command, and every part must match

> Claude Code is aware of shell operators, so a rule like `Bash(safe-cmd *)`
> won't give it permission to run the command `safe-cmd && other-cmd`. The
> recognized command separators are `&&`, `||`, `;`, `|`, `|&`, `&`, and
> newlines.

One unmatched link in a chain prompts for the whole chain. This is why the
agents run separate single commands instead of `&&` chains, and set the test
import path once in `conftest.py` rather than prefixing `PYTHONPATH=...` onto
every command.

Note also that environment runners are **not** stripped wrappers. A rule like
`Bash(devbox run *)` would approve `devbox run rm -rf .`, so a runner rule has
to name the inner command.

Source: [permissions - compound
commands](https://code.claude.com/docs/en/permissions).

### A defensive "if it exists" costs a tool call

`/start` used to open with:

> Read `PROJECT.md` and `session-memory.md` (if it exists).

Both files are imported by `CLAUDE.md`, so both were already in context. The
instruction produced two redundant reads, and the parenthetical produced a third
call: the assistant ran a Glob to check whether the file was there before reading
it. The template always ships `session-memory.md`, so the condition could never
be false.

Two lessons that will recur when writing the Copilot side:

- **Never instruct a read of an imported file.** State that it is already in
  context, so the assistant does not helpfully fetch it again.
- **Do not hedge about files the template guarantees.** "If it exists" reads as
  "verify this", and verifying means searching. The framework's own rule against
  handling impossible scenarios applies to prompts, not just to code.

### Windows command flags get rewritten when run through Bash

On Windows the Bash tool is Git Bash, and MSYS rewrites arguments that look like
absolute POSIX paths into Windows paths. A `/F` flag becomes `F:/`:

```
$ taskkill /F /PID 999999
ERROR: Invalid argument/option - 'F:/'.

$ taskkill //F //PID 999999
ERROR: The process "999999" not found.
```

The second is the command actually working. This bit `/kill`, which stops the app
by PID: run through Bash it failed and left the app running, and the error looked
like a `taskkill` usage problem rather than a shell problem.

Run Windows tools that take `/FLAG` arguments through the **PowerShell tool**,
which does not rewrite them. Doubling the slash also works in Bash but is easy to
drop when someone later edits the command.

### The reloader outlives the PID that netstat reports

`/spawn` runs the app with `--debug`, which starts Werkzeug's reloader: a parent
process plus a child that does the serving. Kill the parent and the child keeps
the socket, so the app carries on answering - and `netstat -ano` can go on naming
the dead parent. Reproduced locally:

```
$ taskkill /F /PID 4644
SUCCESS: The process with PID 4644 has been terminated.

$ netstat -ano | grep 8099
  TCP  127.0.0.1:8099  0.0.0.0:0  LISTENING  4644

$ taskkill /F /PID 4644
ERROR: The process "4644" not found.

$ curl -s 127.0.0.1:8099/health
{"status": "UP"}
```

The processes actually serving were 19204 and 9692. So a `netstat` → `taskkill`
loop spins on a PID that no longer exists while the app stays up, and it reads
like `taskkill` misbehaving rather than the reloader having forked. Stop them by
command line instead; `/kill` step 3 covers it.

`flask run --reload` without `--debug` is not the way out. It does reload Python
changes, but leaves `Debug mode: off`, and Jinja's template auto-reload follows
`app.debug` - so template edits would be served from cache, which is the common
case for a server-rendered template. It also still forks, so the PID problem
above remains either way.

## Python and CodeNow

### `dictConfig` disables existing loggers by default

`logging.config.dictConfig` defaults `disable_existing_loggers` to `true`. Any
logger created before the call is switched off and never logs again, silently.

`src/app.py` runs `dictConfig` at import time, after its own imports. So the
moment a module does the completely ordinary

```python
logger = logging.getLogger(__name__)
```

at import, and is imported from `app.py`, its logs disappear with no error
anywhere. Reproduced locally against the shipped config: the module logger came
back `disabled = True`, and `disabled = False` once the key was set.

The component's `log-config.json` did not set the key. It now does, and the rule
is stated in `rules/codenow.md`.

### Never write runtime data into the application directory

On CodeNow the app directory can be read-only at runtime. A database, cache,
upload folder, or file log created inside it works locally and fails after
deploy, typically as SQLite reporting "unable to open database file".

Writable state goes to a path resolved from an environment variable, defaulting
to a system temp directory. Bundled read-only assets stay in the app directory.

### The IntelliJ run config sets the working directory to `src/`

`.run/Application.run.xml` sets `WORKING_DIRECTORY` to `$PROJECT_DIR$/src`,
which is why the original component could open its log config as
`../codenow/config/log-config.json`. That path is correct only when the process
starts from `src/`, and it breaks under `python src/app.py` from the project
root, which is what `/spawn` and pytest do.

The template resolves the path relative to `__file__` instead, so it works from
either working directory. If a path in the scaffold looks wrong, check what the
run config sets before changing it.

## Process

### A project's copy of the framework is frozen

The framework ships inside the CodeNow component, so a project gets whatever
version the component held on the day its repository was created. Fixes made to
`flask_template/` afterwards do not reach it. Improving the template is only
half the job: the component has to be rebuilt before new projects pick the fix
up, and existing projects never do.
