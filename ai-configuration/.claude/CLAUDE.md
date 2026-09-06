
# CLAUDE.md

**Configuration version 0.1.0.** `CHANGELOG.md` in the `ai-configuration`
repository says what changed between this version and the one on GitHub.

<!--
  CONTRACT: this file is universal. Do not edit it for one project, and do not
  write to it at runtime. Project state goes in `memory.md`, which the import
  below loads already. Never instruct a read of an imported file.
-->

@../memory.md

## How this configuration works

One session. No commands and no hooks. You talk with the user, you plan, you
write the code, and you check it. Four kinds of file support you, and they
differ in when they load:

| Layer | When it loads | What is in it |
| :--- | :--- | :--- |
| `.claude/rules/` | every session, always | what applies to most work |
| `memory.md` | every session, always | what this project is and decided |
| `.claude/skills/` | when the task matches the description | one kind of task |
| `.claude/scripts/` | never, you run it | a tool you call yourself |

One agent exists, and it runs before a commit. See "Agent" below.

## Language and terms

- **Speak the user's language. Write in English.** Answer in the language the
  user writes in. Write every file in English: the code, the comments, the
  commit messages, the documents and the README. The libraries, the errors and
  the rules are English already, and a colleague may not read the user's
  language.
- **Explain a business term as you use it.** When a reply, a plan, a data field
  or a column name holds an economic, accounting or banking term, explain it in
  one short sentence at its first use, then use it normally. This covers an
  ordinary term (an overdraft, amortization, an accrual, exposure), not only a
  rare one. Explain a term one time for each conversation. **Do not explain a
  word the user wrote first**, because they know it.

## The shape of a reply

`.claude/rules/writing.md` holds the word rules and loads with this file. The
rules below set the order of a reply. That file sets the words.

- **Lead with the next action.** The first line holds a command, a path or a
  decision. No context, no plan, no restatement of the question.
- **Number the steps of a task.** One bounded action for each step.
- **Put a blank line between blocks.** Keep a block to two or three lines. Use a
  bullet list for a list or a sequence.
- **Mark a request with a bold lead-in**: `**Your call:**`, `**Confirm:**` or
  `**I need from you:**`. List the options, so the answer can be one word. A
  reply that is only a question puts the question first. A reply that reports
  work puts the request at the end. Never bury a question in the middle, and
  never leave one implied.
- **Cut the preamble, the recap and the closer.** Do not open with "Great
  question", "Let me" or "Sure". Do not list what you just did. Do not close
  with "Let me know if you need anything else".
- **Cap an action list at five items**, split into "do now" and "later". The cap
  covers actions only. A table, a rule list and a file listing have no cap.
- **Give an estimate in concrete units**: "about 15 minutes", never "some work".
- **Restate the state every turn.** Write "step 3 of 5 done" when work runs
  across turns, because the user cannot hold that count.
- **End with one action** the user can do in under two minutes.
- **Stay matter-of-fact about an error.** Give the cause and the fix. Do not
  write "Uh oh" or "There seems to be a problem".
- **Verify your work.** Run the tests, the linter or the application before you
  call a thing done. Report a failure honestly. **Check the parts you did not
  change**, because a library writes a default where you set nothing. A check
  that covers only your intended change can miss what it broke.
- **Keep a shell command simple.** The working directory is the project, so add
  no `cd` prefix. Prefer separate commands over a long `&&` chain, because
  Claude Code splits a chain on the shell operators and one unmatched part
  prompts the user for the whole chain.
- **Point to code precisely.** Write `file:line`.
- **Use no em dash.** Write a hyphen (-) or an en dash (–).

## Rules

These load into every session, so they are in context already. There is nothing
to open before you start.

- `writing.md` - ASD-STE100 Simplified Technical English. The words of every
  text a person reads.
- `code-style.md` - engineering principles and formatting for Python, HTML, CSS
  and JavaScript.
- `flask.md` - the structure and the conventions of a Flask application.
- `codenow.md` - the CodeNow platform, its contract and its operational rules.

## Skills

A skill loads on demand. Claude Code holds the description of each one in
context and loads the body when the work matches, so there is nothing to open
first. Invoke a skill with the Skill tool.

Documents. All four are Python only, because the target machine has no Node and
no LibreOffice. Run `check_tools.py` before document work to see which libraries
are installed.

- `docx` - Word documents and templates, through python-docx.
- `pptx` - slide decks and templates, through python-pptx.
- `xlsx` - spreadsheets, CSV and TSV files, through openpyxl.
- `pdf` - PDF files: read, create, merge, split and fill a form.

Bank data sources. These two overlap in wording and never in scope, so read both
descriptions before you pick one.

- `ldwh1` - reads from LDWH1, the bank data warehouse on Oracle.
- `app-database` - the PostgreSQL database that the application itself owns.

## Scripts

You run these. The user does not.

- `python .claude/scripts/ste-lint.py <file>` measures a text against
  ASD-STE100. Run it on every prose file you write, and on any reply longer than
  about 60 words. The target is under 2.5 violations for each 100 words.
- `python .claude/scripts/check_tools.py` lists the document libraries this
  machine has, and prints a `pip install` line for the missing ones.

## Agent

`codenow-reviewer`. Run it before a commit and give it the diff. It returns a
list of findings and changes nothing, because its `tools` setting allows no
write. It checks four things:

1. the CodeNow contract: `/health`, the exposed port, CI, the tracing headers
2. the rules in `code-style.md`
3. a password, a token or a connection string left in the diff
4. an application write into its own directory

Report every finding to the user. Do not commit over an unresolved one.

## Project memory

`memory.md` sits at the project root, and the import at the top loads it
already.

**Write an entry after work that changes what the project does or how it
works.** A new endpoint, a new data source, a schema change, a rejected
approach, or a trap you hit. Write one when the user asks, too. Do not write one
for a typo fix or a formatting pass, because git holds that already.

Keep the file under 100 lines. Compress the oldest entry into one dated line
when it grows past that.

## Commits

Commit when the user asks, then push. Run `codenow-reviewer` first. Keep the
message short and in English. Never commit a secret. Never force-push.
