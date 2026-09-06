
# About this customization

`.claude/` in this folder configures Claude Code for bank work: building Flask
applications on CodeNow, reading the LDWH1 warehouse, handling Office files, and
writing in plain English.

It is the successor to `flask_template/`. It drops that template's four commands
and two subagents and keeps the knowledge, as rules that always load and skills
that load on demand.

## What is in the folder

```
.claude/
  CLAUDE.md      the operating file: philosophy, reply rules, two indexes
  settings.json  permissions
  rules/         writing.md  code-style.md  flask.md  codenow.md
  scripts/       check_tools.py
  skills/        asd-ste100  docx  pptx  xlsx  pdf
                 ldwh1  app-database  skill-creator
```

217 files, 4.4 MB. Almost all of the size is the Office skills, which carry the
ECMA-376 schemas.

## Three layers, and when each one loads

| Layer | Loads | Cost |
| :--- | :--- | :--- |
| `CLAUDE.md` and `rules/` | every session, always | 542 lines |
| `skills/` | when the model matches a request to a description | about 5 KB of descriptions, the body only on trigger |
| `scripts/` | never, until you run one | nothing |

The split follows one test. A capability is a **rule** when it applies to most
work. It is a **skill** when it applies to one kind of task.

`check_tools.py` reports which document libraries and binaries the machine has.
Several skills hold more than one route to the same result, so run it before
document work rather than assuming.

## Where CLAUDE.md and the skills can fight

They can, and six places are known. A skill body is a reference that one task
loads. `CLAUDE.md` and `rules/` are standing instructions. So:

> **`CLAUDE.md` and `rules/` win on policy. A skill wins on facts about its own
> domain.**

A rule decides how to behave. A skill knows that `TEXTJOIN` needs an `_xlfn.`
prefix, and no rule overrides that.

### 1. `skill-creator` assumes subagents. This setup has none.

`CLAUDE.md` opens with "no subagents and no commands". `skill-creator/SKILL.md`
names a subagent 13 times and builds its whole evaluation loop on them:

> For each test case, spawn two subagents in the same turn, one with the skill,
> one without.

**Ruling: `CLAUDE.md` wins.** Write and edit skills with `skill-creator`, and
treat the evaluation and benchmark sections as unavailable. Run a test case in
the session instead, one at a time, and accept that it is weaker evidence. The
skill says so itself for Claude.ai, which also has no subagents.

This is the sharpest conflict in the folder.

### 2. `asd-ste100` describes hooks that are not installed.

The skill assumes its four hooks are armed. Two lines act on that:

- `SKILL.md:181` says a gate lints the reply after you send it.
- `SKILL.md:198` says what to do "if the gate blocks you anyway".

Neither happens here. The hooks were deliberately left out, because they call
`python3`, which stock Windows lacks, and the `Stop` gate can send a reply twice.

**Ruling: ignore both lines.** Lint a draft yourself with the command in
`rules/writing.md`. Nothing checks a reply after you send it.

### 3. The reply rules and the skill disagree about the closer.

`asd-ste100` forbids a closer. `CLAUDE.md` requires a marked request at the end
of a reply that reports work, with a bold lead-in and the options listed.

**Ruling: `CLAUDE.md` wins, and the disagreement is deliberate.** A question that
is not marked gets skimmed past, and then the user does not know it is their
turn. The skill's own "End with one action" rule points the same way. Everything
else in Layer 2 was adopted as written.

### 4. Three rule files break the writing rule that sits beside them.

`rules/writing.md` bans the semicolon and the contraction. The three rule files
carried over from `flask_template` are full of both:

| File | Semicolons | Contractions |
| :--- | :--- | :--- |
| `code-style.md` | 10 | 4 |
| `flask.md` | 10 | 1 |
| `codenow.md` | 7 | 4 |
| `writing.md` | 0 | 1, as a counter-example |

**Ruling: the rule governs new text.** Write every new sentence in Simplified
Technical English. Do not rewrite those three files for style alone, because a
style-only rewrite of a working rule file risks changing its meaning for no gain.
Fix the prose of a section when you edit that section for another reason.

### 5. Every skill carries em dashes. The house rule bans them.

| Skill | Em dashes |
| :--- | :--- |
| `pptx` | 64 |
| `skill-creator` | 45 |
| `asd-ste100` | 20 |
| `xlsx` | 17 |
| `docx` | 13 |

**Ruling: no real conflict.** The rule governs what you write, not what you read.
The four skills written here (`ldwh1`, `app-database`, and both `references/`
files) carry none.

### 6. `pptx` collides with a skill of the same name.

Claude Code ships a `pptx` skill. This folder ships another. When both are
visible, the local one is renamed to `ai_bank_setup:pptx` and the two are offered
side by side.

**Ruling: name the skill explicitly** when the difference matters. The local copy
is the one that knows this machine has no LibreOffice and no Node, and it carries
`references/python-pptx.md` and `scripts/repack.py`. The built-in copy does not.

Nothing else in the folder collides.

## One more thing about scope

Inside this repository the skills are scoped to `ai_bank_setup/`, so they apply
only to work on files under this folder. Copy `.claude/` to the root of a real
project and the scoping disappears, because the folder is then the project.

## What was checked

| Check | Result |
| :--- | :--- |
| all 8 skills parse and carry a name and a description | pass |
| a full Word document built from `references/python-docx.md` | passes the ECMA-376 schema check |
| a full deck built from `references/python-pptx.md` | passes |
| `repack.py` round trip on a document and a deck | both validate, and the edit reads back |
| every prose file written here, on `ste-lint.py` | 0.84 to 1.87, target 2.5 |

Three bugs were fixed in the copied skills: two Windows encoding faults that made
every document fail validation, and a linter that counted possessives as
contractions.

**Not checked: whether a skill fires for the right prompt.** That needs a live
session, and no static check reaches it. `ldwh1` against `app-database` is the
pair most likely to catch each other's work.

## Where the parts came from

| Part | Origin |
| :--- | :--- |
| `CLAUDE.md`, `rules/writing.md`, `ldwh1`, `app-database`, both `references/`, `check_tools.py`, `repack.py` | written for this folder |
| `rules/code-style.md`, `flask.md`, `codenow.md` | `flask_template/`, four dead references removed |
| `docx`, `pptx`, `xlsx`, `pdf`, `skill-creator` | Anthropic skills, plus an Environment section and bug fixes |
| `asd-ste100` | MIT, by Ege Chelebi, without its hooks |

`docs/5_ai_bank_setup.md` in the repository root holds the full design and the
open items.
