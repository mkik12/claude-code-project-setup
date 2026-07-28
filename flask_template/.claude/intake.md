# Project intake questions

**Read-only.** This is the question script `/start` works from on first run, not a
form to fill in. Never write answers here. Every answer has a durable home
elsewhere, and duplicating it into this file would only create a second version
that can disagree with the first:

| Question | Where the answer goes |
| :--- | :--- |
| q1 language | `PROJECT.local.md` (per person, gitignored) |
| q2 starting point | `session-memory.md`, as the route the setup took |
| q2b what we are building | `PROJECT.md`, as the "## Overview" |
| q3 input materials | `PROJECT.md`, named in the "## Overview" |
| q4 who commits | `PROJECT.local.md` (per person, gitignored) |

Ask them one at a time, in the user's language. q2 has its own routes; `/start`
describes them.

### q1 - Language

Which language should I use when talking with you?

### q2 - Starting point

Which of these fits you best?

- **(a)** You know what we are building - tell me everything you have.
- **(b)** Not sure yet - let's work it out together.
- **(c)** You have a working app to move onto this framework - add the files and
  I will read them.

### q2b - What we are building

Not asked directly. This is the summary produced by whichever route q2 took, read
back to the user and confirmed by them. In route (c) it is also the specification
the rewrite works from.

### q3 - Input materials

Do you have any input materials the app needs (e.g. Excel files, images,
documents)?

### q4 - Saving code to the repository

Who should save the code to the online repository (GitHub, GitLab, Bitbucket) -
you or me? (In technical terms, that's the commits and pushes.)
