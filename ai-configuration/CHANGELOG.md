
# Changelog

This file answers one question. You hold version 0.1.0, GitHub holds a later
one, and you want to know whether a fresh copy is worth the effort.

Newest version at the top. The version number also sits in `CLAUDE.md`, right
under the heading.

| Number | When it goes up |
| :--- | :--- |
| PATCH `0.1.1` | a fix, nothing new |
| MINOR `0.2.0` | something new, and the old behaviour still works |
| MAJOR `1.0.0` | the new folder over the old one breaks something |

## 0.1.0

The first version. Everything below is new.

**The core.**

- `CLAUDE.md`, which holds the version, the three layers, the shape of a reply,
  the language rule and the business-term rule.
- `settings.json`, with the permissions written twice, once for Bash and once
  for PowerShell. They are two rule namespaces, and a rule for one does nothing
  for the other.
- `memory.md`, an empty template for the project memory. It sits at the project
  root, because `.claude/` is a protected path and a write there always asks for
  confirmation.

**Four rules, always loaded.**

- `writing.md` - ASD-STE100 Simplified Technical English.
- `code-style.md` - Python, HTML, CSS and JavaScript.
- `flask.md` - the structure of a Flask application.
- `codenow.md` - the CodeNow contract and the operational rules.

**Six skills, loaded on demand.**

- `docx`, `pptx`, `xlsx` and `pdf`, all Python only. The target machine has no
  Node and no LibreOffice, so no skill offers a route through either.
- `ldwh1` for the bank data warehouse on Oracle, in thin mode only.
- `app-database` for the PostgreSQL database the application owns.

**One agent.** `codenow-reviewer` reads a diff before a commit and returns
findings. Its `tools` setting holds no write tool.

**Two scripts.** `ste-lint.py` measures a text against ASD-STE100.
`check_tools.py` reports which document libraries this machine has.

### Known limits in 0.1.0

- **No skill was triggered in a live session.** Each file is well formed. That
  does not prove the right skill loads for the right question, and `ldwh1`
  against `app-database` is the pair most likely to take each other's work.
- **This configuration ships no file validator.** The ECMA-376 schemas are
  1.2 MB against a 200 kB budget, so nothing checks the structure of a `.docx`
  or a `.pptx` before a person opens it. Word and PowerPoint did open the test
  files that the `docx` and `pptx` code produces, and that check found a layout
  defect the code had: a 16:9 deck kept the 4:3 placeholder geometry of the
  default template. The `pptx` skill now carries `fit_placeholders` for it. The
  Word side needed no fix. The table of contents filled, the `PAGE` and
  `NUMPAGES` fields resolved, and the table and the styles came out right.
  Read a generated file back, then ask the user to open it.
