
# The skills setup (ai_bank_setup)

The framework's second deliverable, and the successor to `flask_template/`. It
answers a wider question than the template does: not only "build me a Flask app
on CodeNow", but also "work with my Office files", "read the warehouse", and
"explain this finance term to me".

Read `2_workflow.md` first for the original design. This document only covers
where this deliverable departs from it.

## What changed, and why

`flask_template/` drives a session with four commands and two subagents. That
machinery exists to take a non-technical colleague from a plain-language
description to a committed application. It is the right shape for that job and
the wrong shape for daily work, where the user already knows what they want and
the ceremony gets in the way.

So this deliverable drops the machinery and keeps the knowledge.

| | `flask_template/` | `ai_bank_setup/` |
| :--- | :--- | :--- |
| Commands | `/start` `/spawn` `/kill` `/end` | none |
| Subagents | `planner`, `coder` | none |
| Interview | `intake.md`, four questions | none |
| Cross-session memory | `PROJECT.md`, `session-memory.md`, `PROJECT.local.md` | none |
| Always-on rules | 3 files | the same 3 files |
| On-demand skills | none | 8 |
| Reply style | its own rules | ASD-STE100, via the `asd-ste100` skill |

Dropping the memory files is what let the commands go: `/start` and `/end` were
the only things that wrote them. Every session now starts cold, which is the
accepted cost.

## Layout

`ai_bank_setup/.claude/` is a drop-in configuration for a project that already
holds a CodeNow scaffold. It ships no `src/`, no `tests/` and no
`.codenow.yaml`, so `rules/flask.md` refers to files that exist at the
destination rather than in this folder.

~~~
.claude/
  CLAUDE.md      philosophy, working rules, the finance-term rule, two indexes
  settings.json  permissions, identical to the template's
  rules/         writing.md  code-style.md                always on
                 codenow.md  flask.md
  scripts/       check_tools.py                           run by hand
  skills/        asd-ste100  docx  pptx  xlsx  pdf
                 ldwh1  app-database  skill-creator       on demand
~~~

211 files, 4.2 MB. Almost all of it is the Office skills: `scripts/office/` is
byte-identical in `docx`, `pptx` and `xlsx`, about 1.2 MB of ECMA-376 schemas
each, and the copies were kept rather than deduplicated so upstream updates stay
a straight drop-in.

## A standing style rule cannot be a skill

A skill loads on demand. ASD-STE100 is a standing rule, and its own description
says so: "A standing style rule, not an on-request tool." Those two facts
conflict, and the conflict is not cosmetic. A rule that governs every sentence
cannot wait for the model to decide it is relevant.

Measuring it showed the split was already half right by accident:

| Half | Where it lives | Always on |
| :--- | :--- | :--- |
| Layer 2, the shape of a reply | `CLAUDE.md` working rules | yes, 8 rules |
| Layer 1, the words | nowhere | no |

Every Layer 1 marker was absent from the always-on context: active voice, simple
tenses, the semicolon ban, phrasal verbs, compound nouns, the 20-word cap, the
contraction ban, the word substitutions. The shape of a reply was guaranteed. The
words were not.

`rules/writing.md` closes that. A rule file loads at every session with no model
judgment involved, which is the only mechanism here that gives a guarantee. The
alternatives were each worse:

- **The upstream output style** installs to `~/.claude/output-styles/` and sets
  `outputStyle` in the user's own `settings.json`. It does not ship inside a
  project, so every colleague would have to run an installer.
- **The upstream hooks** are deterministic, but they call `python3`, and the
  `Stop` gate can send a reply twice.
- **A stronger pointer to the skill** would still depend on the model choosing
  to load it, which is the thing that failed.

The skill stays, with a narrower job: the full specification, the linter, and the
review and rewrite modes. `CLAUDE.md` now says the rules are already loaded and
names the skill for those three uses only.

Always-on context went from 393 lines to 542. That is the price, and it buys a
guarantee rather than a probability.

## Rules against skills

Rules load into every session. Skills load when the work matches their
description. That distinction is the whole reason this deliverable is possible:
the eight skills hold roughly 1500 lines between them, and as rule files they
would have quadrupled the always-on context.

A capability is a **rule** when it applies to most work (how to write Python,
what CodeNow requires). It is a **skill** when it applies to one kind of task
(build a deck, read the warehouse).

The finance-term requirement went the other way, into `CLAUDE.md`, because it is
neither: it is a habit that has to fire whenever a term appears, and a skill only
triggers on task shape.

## The skills

| Skill | Source | Built how |
| :--- | :--- | :--- |
| `asd-ste100` | `resources/asd-ste100/` | copied, hooks left out |
| `docx` `pptx` | `resources/` | copied, plus an Environment section and a Python reference file |
| `xlsx` | `resources/xlsx/` | copied, plus an Environment section |
| `pdf` | `resources/pdf/` | copied verbatim |
| `skill-creator` | `resources/skill-creator/` | copied, one encoding bug fixed |
| `ldwh1` | `resources/ldwh1_connection.md` | written from the spec |
| `app-database` | `resources/db_connection.md` | written from the spec |

`asd-ste100` ships the skill, the linter and the references, but **not** its four
hooks, `install.py` or the output style. The hooks call `python3`, which stock
Windows does not have, and its `Stop` gate can make a reply send twice. The skill
plus the linter gives the writing system without running third-party code on
every turn.

`app-database` is documentation only. It changes no rule file, adds no
dependency and does not touch the scaffold, so a project that never needs
persistence carries nothing for it.

## Changes to the copied material

Four dead references, from removing the commands and the subagents:

- `rules/code-style.md:4-5` and `:66` named the planner and the coder.
- `rules/flask.md:72` named `/spawn`.
- `skills/asd-ste100/SKILL.md:186` and `:191-193` called `python3` and pointed at
  a user-level install path.

Then two bug fixes, two new reference files, and three rewritten sections,
described below.

## Two Windows encoding bugs, fixed

Both were the same mistake, and both were found by running the tools rather than
by reading them.

**`office/validators/base.py:786` opened part XML in text mode with no
encoding.** On Windows that decodes with the ANSI codepage, so any part holding a
byte the codepage lacks raised a `charmap` decode error, which the validator then
reported as a schema error. `word/fontTable.xml` in python-docx's own default
template holds such a byte, so every document failed validation on Windows. The
fix is to open in binary, which is also how lxml wants it: `lxml.etree.parse`
then honours the XML declaration. Applied in all three copies of the `office/`
tree.

**`skill-creator/scripts/quick_validate.py:22` called `read_text()` with no
encoding**, for the same result. It killed the `pdf` skill on the subscript
characters in its body. Fixed to `read_text(encoding="utf-8")`. That skill was
otherwise copied verbatim, but this tool is the only skill validator and it
reported a false failure on every run.

Both matter more than they look. With LibreOffice out, the XSD check is the only
verification left for a `.docx` or a `.pptx`, and it was failing every time for a
reason that had nothing to do with the file.

## Two linter bugs, and the missing zip

**`ste-lint.py:172` counted every possessive as a contraction.** The regex
allowed a bare `'s`, so `the user's language` scored a violation. A trailing
`'s` is a contraction only after a closed set of function words (`it's`,
`that's`, `there's`). The fix splits the pattern in two and keeps a possessive
clean, which STE permits.

**`ste-lint.py:186` counted an en dash as an em dash.** STE bans neither, and
the house rule allows an en dash, so the count reported a violation that does
not exist. It now counts only U+2014.

Four test cases confirm both fixes: two possessives score 0, three real
contractions score 3, an en dash scores 0, and an em dash scores 1.

**`zip` is missing while `unzip` is present**, which stopped the
unpack-edit-repack loop halfway in `docx` and `pptx`. Both skills now ship
`scripts/repack.py`, standard library only. It writes a fresh archive so a
deleted part does not survive, and it puts `[Content_Types].xml` first.

The round trip was tested both ways: unpack, edit the XML, repack, validate, and
read the edit back with the library. A Word file and a deck both passed. The test
also caught its own mistake usefully: deleting a part without its relationship
produced a broken package, and `validate.py` reported exactly that.

One more `python3` call turned up in `pptx/SKILL.md:84` and is now `python`.

## The Node-free creation route

`docx` creates documents with docx-js and `pptx` builds decks with pptxgenjs.
Both are Node libraries and `node` is absent, so each skill gained a reference
file covering the same work in Python:

- `skills/docx/references/python-docx.md`
- `skills/pptx/references/python-pptx.md`

Every snippet in both was executed, and both outputs passed
`office/validate.py`. Three gotchas came out of doing that rather than
remembering it:

1. **A Word field does not refresh by itself.** A `TOC` renders blank without the
   `w:updateFields` setting. `CT_Settings` is an ordered sequence, so appending
   that element to `settings.xml` gives "this element is not expected" and an
   invalid file. The correct successors were read out of the bundled `wml.xsd`,
   and the reference inserts the element before them.
2. **python-docx writes a `w:zoom` element with no `percent`.** The attribute is
   required, so every document from the default template failed the schema until
   the reference set it. Word tolerates the omission, which is how the library
   gets away with it.
3. **python-pptx writes chart XML that PowerPoint opens.** pptxgenjs writes chart
   XML that PowerPoint refuses and every other tool accepts. So the Python route
   is better here, not merely a fallback.

## Capability detection, not a hardcoded machine

`.claude/` is shared, so the next person has a different machine. Two things
follow.

`scripts/check_tools.py` reports what is present: twelve binaries and thirteen
Python packages, each with a line saying what it is for, and a ready-made
`pip install` line for whatever is missing. It always exits 0, because a missing
tool is information rather than a failure.

It also guards a trap worth naming. A directory named `docx` or `pptx` imports as
a namespace package, so `import pptx` from inside `.claude/skills/` succeeds and
returns the skill folder instead of the library. That produced a false positive
during this work: python-pptx looked installed when it was not. The check treats
a `__file__` of `None` as absent and says why, and that guard was tested against
a folder-only name.

The `docx`, `pptx` and `xlsx` skills each open with an `## Environment` section
that branches rather than asserts. Each names the condition, the route that fits
it, and the current default, then says to check rather than assume.

## Thin mode only, for LDWH1

`oracledb` thin mode is the only supported mode. It is pure Python and needs no
Oracle Client library, which settles the question the CodeNow runtime image
raised: the slim Python image carries no client, and now nothing asks it to.

The skill states this, shows a thin-mode `get_connection`, and lists a call to
`init_oracle_client()` among the changes it must refuse. A requirement that
genuinely needs thick mode is a platform decision, and the skill says to stop and
escalate rather than write the call.

## Verified

Run, not asserted:

| Check | Result |
| :--- | :--- |
| `quick_validate.py` on all 8 skills | 8 valid, `pdf` included after the fix |
| `office/validate.py` on a full python-docx document | passed, with a TOC, `PAGE` and `NUMPAGES`, tables, styles, bullets and margins |
| `office/validate.py` on a full python-pptx deck | passed, with 16:9, layouts, nested bullets, notes, a table, a native chart and an image |
| `ste-lint.py` on `CLAUDE.md` | 1.34 per 100 words, target 2.5 |
| `ste-lint.py` on `rules/writing.md` | 1.81, after fencing the word lists |
| `ste-lint.py` on `ldwh1` and `app-database` | 1.25 and 1.87 |
| `repack.py` round trip on a document and a deck | both validate, and the edit reads back |
| `ste-lint.py` on both reference files | 1.55 and 0.84 |
| dead references outside `skills/` | none |
| the `check_tools.py` shadowing guard | rejects a folder-only name, accepts a real package |

The scores above are lower than the ones first measured, because the two
`ste-lint.py` false positives are fixed rather than merely documented.

## The tooling that is actually present

Measured with `check_tools.py`, not assumed.

| | Present | Absent |
| :--- | :--- | :--- |
| Binaries | `git`, `unzip`, `pdftotext` | `soffice`, `node`, `npm`, `pandoc`, `pdftoppm`, `pdfimages`, `qpdf`, `zip`, `tesseract` |
| Python | `python-docx`, `python-pptx`, `openpyxl`, `pandas`, `pypdf`, `pdfplumber`, `reportlab`, `Pillow`, `lxml`, `defusedxml`, `markitdown` | `oracledb`, `psycopg` |

The Python packages were installed during this work, which is what made the
recipes verifiable. `oracledb` and `psycopg` stay out until an application needs
them, because they belong in that project's `requirements.txt` rather than on a
laptop.

`zip` is missing while `unzip` is present. `scripts/repack.py` in `docx` and
`pptx` closes that gap with the standard library.

## Open items

1. **No live session has exercised the skill triggers.** Validation proves each
   file is well-formed. It does not prove the right skill loads for the right
   prompt, and `ldwh1` against `app-database` is the pair most likely to catch
   each other's work.
2. **The Python creation routes are validated, not reviewed by a person.** A
   document can pass every schema check and still look wrong, and without a
   renderer nobody has looked at one. Open a generated file in Word and in
   PowerPoint once.
3. **No Copilot mirror.** `ai_bank_setup/.github/` is empty. Copilot has no
   on-demand skill mechanism, so a mirror means turning every skill into an
   always-on `applyTo` instruction or dropping it. That is a fourth divergence
   from the "change both assistants or neither" rule in `SESSION-BRIEFING.md`,
   and it is deliberate.
Settled, and needing no further work: LibreOffice is out and the three Office
skills branch on its absence; LDWH1 uses thin mode only; the Node-free creation
routes exist and are verified. Business knowledge needed no skill at all, because
the requirement was ordinary economic vocabulary rather than RBCZ jargon, so it
became a working rule in `CLAUDE.md`.
