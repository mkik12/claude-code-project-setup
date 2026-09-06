
# ai-configuration

A Claude Code configuration for a technical developer at the bank. It adds the
knowledge Claude does not have: the CodeNow platform, the LDWH1 data warehouse,
the application database, MS Office files and PDF files.

Copy it into your project, or leave it alone. Nothing here is mandatory.

**Version 0.1.0.** `CHANGELOG.md` holds the history.

## What to copy

Two things, not one:

```
.claude/      the configuration
memory.md     an empty template for the project memory
```

`memory.md` sits at the project root, next to `.claude/` and not inside it.
`.claude/` is a protected path in Claude Code, so a write there asks for
confirmation every time and no settings entry turns that off. Claude writes the
project memory during a session, so the file must sit outside.

`CLAUDE.md` imports `memory.md`. Copy only one of the two and the import points
at nothing.

`task.md`, `README.md` and `CHANGELOG.md` stay in this repository. Your project
does not need them.

## How to copy

From the root of your project, with this repository cloned next to it:

```powershell
Copy-Item -Recurse ..\ai-configuration\.claude .
Copy-Item ..\ai-configuration\memory.md .
```

```bash
cp -r ../ai-configuration/.claude .
cp ../ai-configuration/memory.md .
```

Then commit both. They are shared team files, and `memory.md` is the shared
memory of the project.

## After the first copy

1. **Accept the workspace trust dialog** the first time Claude Code opens the
   project. Until you do, the `allow` rules in `.claude/settings.json` are read
   and not applied, so every command asks for permission. Trust is keyed on the
   git repository root.
2. **Run `python .claude/scripts/check_tools.py`.** It lists the document
   libraries this machine has, and prints a `pip install` line for the missing
   ones. `oracledb` and `psycopg` belong in the project `requirements.txt`, not
   on your laptop, so install them only when the application needs them.

## What is inside

```
.claude/
  CLAUDE.md        the core: version, layers, reply shape, language rule
  settings.json    permissions, written twice for Bash and for PowerShell
  rules/           writing.md  code-style.md  flask.md  codenow.md
  agents/          codenow-reviewer.md
  skills/          docx  pptx  xlsx  pdf  ldwh1  app-database
  scripts/         ste-lint.py  check_tools.py
memory.md          the project memory, written by Claude
```

Three layers, and they differ in when they load. A **rule** loads in every
session, so it holds what applies to most work. A **skill** loads when the task
matches its description, so it holds one kind of task. A **script** never loads.
Claude runs it.

`CLAUDE.md`, the four rules and `memory.md` together are about 600 lines, which
is what every session carries.

## The target machine

Python and git, and nothing else. No Node, no LibreOffice, no `zip`, no
`pandoc`, no `tesseract`. The document skills use `python-docx`, `python-pptx`,
`openpyxl`, `pypdf`, `pdfplumber` and `reportlab`, and they offer no route
through a tool that is absent.

One consequence: nothing renders a document, a deck or a PDF, so no skill can
check a layout. Each one says so and asks you to open the file.

## Updating

A copy freezes. A fix made here does not reach a project that copied an earlier
version. Two things keep that manageable:

- the version number in `CLAUDE.md`, right under the heading
- `CHANGELOG.md`, newest version at the top

Compare the two numbers, read the entries between them, and decide whether a
fresh copy is worth it.

Note what follows from committing the configuration: everybody who clones the
project gets it. The choice to take it or not happens one time, when somebody
introduces it into the project.

## Where the material came from

The four document skills are distilled from the Anthropic Agent Skills for
`docx`, `pptx`, `xlsx` and `pdf`. The scripts and the schemas are left out, and
what remains is the traps and the working procedures.

`rules/writing.md` and `scripts/ste-lint.py` come from the ASD-STE100 skill, and
the linter carries two fixes: a possessive is no longer counted as a
contraction, and an en dash is no longer counted as an em dash.
