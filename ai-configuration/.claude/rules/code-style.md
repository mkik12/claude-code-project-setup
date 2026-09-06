
# Code style

Engineering principles and formatting for the code you write. This file loads
into every session, so the rules apply before you write the first line.

## Principles

- **Keep it simple.** Write the smallest amount of code that solves the problem.
  Add no speculative feature, no abstraction for code that runs in one place,
  and no configuration that nobody asked for.
- **A dependency is a cost.** Prefer the standard library and the dependencies
  that are there already. Ask before you add a new one.
- **Handle the errors that can happen.** Cover a realistic failure. Do not guard
  against a case that cannot occur.
- **Never hardcode a secret.** No credential, token, or key in the source or in
  a log line.
- **Match an existing codebase.** When a codebase already has conventions,
  follow them. That covers the structure, the names, the idioms and the
  formatting, even where they differ from the rules below. When the conventions
  are unclear, ask whether to apply these rules instead.

## Python

- **Naming.** `snake_case` for a function, a variable and a module.
  `PascalCase` for a class, such as a Pydantic model or an `Enum`.
  `UPPER_SNAKE_CASE` for a module-level constant.
- **Docstrings.** Google style for a module and a public function. A private
  function takes a one-line docstring and a `_` name prefix.
- **Explicit imports.** No `from X import *`.
- **Two blank lines** between top-level definitions, and one blank line between
  methods, per PEP 8.
- **Return early.** An early return beats deep nesting.
- **Line length.** 79 characters at most for code, and 72 for a comment or a
  docstring.
- **A name says what it means.** Choose a clear, descriptive name over a clever
  or shortened one.
- **A comment explains why, not what.** Do not narrate code that speaks for
  itself, and do not leave a commented-out block.
- **Fix a typo at the source.** When you touch a symbol with a typo in its name,
  rename it. Do not carry the mistake forward.
- **Frame every code file with blank lines.** Start and end each file with one
  empty line.

## HTML

- Use a semantic element (`header`, `nav`, `main`, `section`, `footer`) over a
  generic `div` where one fits.
- One Jinja `base.html` in `templates/`. A page extends it and fills a named
  block. Keep the logic in the backend, not in the template.
- Always set `lang` on `<html>` and include `<meta charset="utf-8">`.
- Point to a static asset with `url_for('static', ...)`, never with a hardcoded
  path.

## CSS

- Plain CSS in `static/css/`. No preprocessor and no framework.
- A class selector with a kebab-case name (`.user-card`). Avoid an ID selector
  for styling, and avoid an inline style.
- Group the related rules. Use a CSS custom property (`--color-...`) for any
  value that appears more than one time.

## JavaScript

- Plain, modern JavaScript in `static/js/`. No framework and no build step.
- `const` and `let`, never `var`. `===` over `==`. A `camelCase` name.
- Put a page script at the end of `<body>`, or in a module under `static/js/`.
- Keep the DOM logic small. When a page needs heavy interaction, think again
  about the template choice.

## Git hygiene

Keep a generated file and a local file out of version control. The project
`.gitignore` covers at least:

- **Virtual environment:** `.venv/`, `venv/`, `env/`
- **Bytecode and cache:** `__pycache__/`, `*.py[cod]`, `.pytest_cache/`,
  `*.egg-info/`
- **Test and coverage:** `.coverage`, `coverage.xml`, `htmlcov/`
- **Secret and local config:** `.env`, `*.env`
- **Local runtime data:** `*.log`, `*.sqlite3`
- **OS and editor cruft:** `.DS_Store`, `Thumbs.db`, `.idea/`

On CodeNow the component ships its own `.gitignore`. Add a missing entry to it
rather than replacing it. Never commit a secret or a virtual environment.
