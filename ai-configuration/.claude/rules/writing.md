
# Writing

Every text a person reads uses ASD-STE100 Simplified Technical English. This file
holds the word rules and loads into every session, so the rules apply before you
write anything.

`CLAUDE.md` holds the shape of a reply. This file holds the words. There is no
skill to load and nothing to open first. `.claude/scripts/ste-lint.py` measures a
draft against these rules.

## Scope

| Text | These rules apply |
| :--- | :--- |
| A reply to a person | yes |
| A commit message, a task, a pull request | yes |
| A README, a document, a release note | yes |
| An error message, a runbook, safety text | yes, strictly |
| Code, an identifier, command syntax, log output | no |

Numbers in parentheses are rule numbers in ASD-STE100 Issue 9.

## Words

- **One name for one thing** (1.11, 9.4). Do not rotate check, verify, validate
  and confirm for the same action. Pick one name and reuse it.
- **One meaning for each word** (1.3).
- **American spelling** (1.14).
- **The short common word.** Use the left column, never the right one.

```text
start      not begin, commence, initiate
use        not utilize, leverage
help       not facilitate
make sure  not ensure, verify
do         not perform, conduct
give       not provide, supply
before     not prior to
after      not subsequent to
about      not regarding, concerning
get        not obtain, acquire
show       not demonstrate
also       not additionally, furthermore, moreover
but        not however
```

- **No marketing adjective.**

```text
seamless    robust       powerful          cutting-edge
effortless  world-class  next-generation   revolutionary
```

## Verbs

- **Active voice.** Write "the parser reads the file", not "the file is read by
  the parser". A procedure is always active. Descriptive text may use the passive
  when the actor is unknown (3.6).
- **Simple tenses only** (3.2): infinitive, imperative, simple present, simple
  past, simple future. Write "we received the report", never "we have received
  the report".
- **No stacked auxiliary** (3.4). Write "this improves X", not "it is important
  to note that this may help to improve X".
- **A verb for an action** (3.7). Write "analyze the log", not "perform an
  analysis of the log".
- A past participle used as an adjective is correct and is not passive (3.3):
  "the field is required".
- **No phrasal verb** (9.3).

```text
spin up  dive into  kick off  roll out  reach out  drill down
```

## Sentences

- **One instruction for each sentence** (5.2), unless two actions happen at the
  same time.
- **20 words at most for an instruction** (5.1). **25 at most for other text**
  (6.3).
- **Put a comma after a condition** that comes before its command (5.4): "If the
  test fails, read the log."
- **Keep the articles** (4.2, 4.5). Write "remove the bolts from the panel",
  never "remove bolts from panel". A general statement about an abstract concept
  takes no article.
- **No contraction.** Write "do not", not "don't". A possessive is correct.
- **Connect related sentences** with then, but, thus, or as a result (4.4). STE
  gives you short sentences, not disconnected ones.

## Nouns and punctuation

- **Three words at most in a compound noun** (2.1). Unpack "the agent task queue
  priority handler" into "the handler that sets task-queue priority".
- **Define an abbreviation at its first use**, then use the abbreviation.
- **No semicolon** (8.1). Write two sentences.
- **One topic for each paragraph** (6.5), six sentences at most (6.6).

## Two modes

- **Strict** for a procedure, a runbook, safety text, or an error message. Apply
  every rule and both length caps. Add: because (not since), can (not may), must
  (not should), obey (not follow).
- **Flavored** for other prose. Apply the sentence, tense, voice, compound-noun
  and phrasal-verb rules. Relax the approved word list, so the text keeps enough
  range to read naturally.

Flavored is the default.

## A list item can stay a label

A flow list, a changelog line, or a feature bullet may be a label and not a
sentence. Keep it short: "Frontend receives session JWT". Do not expand a label
into a sentence only to add an article.

## Guards

- **Never drop a fact, a number, a condition, or a scope qualifier** to meet a
  length cap. Keep the longer sentence and say why.
- **Keep an identifier, a unit, an error string and safety wording exactly.**
- Cut a hedge that carries no fact ("perhaps", "arguably"). Keep a qualifier that
  bounds a claim ("on Windows only", "measured one time").

## Lint a draft before you send it

Run the linter on any prose longer than about 60 words, and on every prose file
you write:

```bash
python .claude/scripts/ste-lint.py draft.md
```

The target is under 2.5 violations for each 100 words, or under 1.5 in strict
mode. Fix the reported categories, lint one more time, then stop. Two passes,
no more. Report the score with the text, and never call a text clean without a
lint run.

This file scores 1.65. Four of its violations are the counter-examples that the
rules above need, one word each: a contraction, a passive clause, a complex
tense, and a nominalization. Do not delete them to lower the score, because the
rule then loses the example that makes it clear. The word lists sit in fenced
blocks for the same reason: the linter strips a fenced block, so a list of
forbidden words does not count against the file that forbids them.
