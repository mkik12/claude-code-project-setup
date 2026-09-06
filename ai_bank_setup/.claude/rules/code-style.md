
# Code style

Engineering principles and formatting for the code you write. Read this file
before you write code.

## Principles

- **Simplicity first.** Write the minimum code that solves the problem - no
  speculative features, abstractions, or configurability that wasn't asked for.
- **Dependencies are a cost.** Prefer the standard library and existing
  dependencies. Ask before adding a new one.
- **Errors that can actually happen.** Handle realistic failure modes; don't
  guard against the impossible.
- **Never hardcode secrets.** No credentials, tokens, or keys in source or logs.
- **Match an existing codebase.** When conventions are already established,
  follow the existing structure, naming, idioms, and formatting even where they
  differ from the rules below. When they are unclear or inconsistent, ask whether
  to apply these rules instead.

## Python

- **Naming.** `snake_case` for functions, variables, and modules; `PascalCase`
  for classes (e.g. Pydantic models and `Enum` classes); `UPPER_SNAKE_CASE` for
  module-level constants.
- **Docstrings.** Google style for modules and public functions. Private
  functions take a one-line docstring and a `_` name prefix.
- **Explicit imports.** No `from X import *`.
- **Two blank lines** between top-level function and class definitions (one
  blank line between methods), per PEP 8.
- **Early returns over deep nesting.**
- **Line length.** Limit code lines to 79 characters; comments and docstrings to
  72.
- **Names say what they mean.** Clear, descriptive names over clever or
  abbreviated ones.
- **Comments explain why, not what.** Don't narrate code that speaks for itself;
  don't leave commented-out blocks.
- **Fix typos at the source.** When you touch a symbol with a typo, rename it
  rather than propagate the mistake.
- **Frame every code file with blank lines.** Start and end each file with one
  empty line.

## HTML

- Use semantic elements (`header`, `nav`, `main`, `section`, `footer`) over
  generic `div`s where they fit.
- One Jinja `base.html` in `templates/`; pages `extend` it and fill named
  blocks. Keep logic in the backend, not in templates.
- Always set `lang` on `<html>` and include `<meta charset="utf-8">`.
- Reference static assets with `url_for('static', ...)`, never hardcoded paths.

## CSS

- Plain CSS in `static/css/` - no preprocessors or frameworks.
- Class selectors with kebab-case names (`.user-card`); avoid ID selectors for
  styling and avoid inline styles.
- Group related rules; use CSS custom properties (`--color-...`) for any value
  used more than once.

## JavaScript

- Plain, modern JavaScript in `static/js/` - no frameworks and no build step.
- `const`/`let`, never `var`; `===` over `==`; `camelCase` names.
- Put page scripts at the end of `<body>` or in a module under `static/js/`.
- Keep DOM logic small. If a page needs heavy interactivity, reconsider the
  template choice.

## Git hygiene

Keep generated and local files out of version control. The project's
`.gitignore` should cover at least:

- **Virtual environment:** `.venv/`, `venv/`, `env/`
- **Bytecode and caches:** `__pycache__/`, `*.py[cod]`, `.pytest_cache/`,
  `*.egg-info/`
- **Test and coverage:** `.coverage`, `coverage.xml`, `htmlcov/`
- **Secrets and local config:** `.env`, `*.env`
- **Local runtime data:** `*.log`, `*.sqlite3`
- **OS and editor cruft:** `.DS_Store`, `Thumbs.db`, `.idea/`

On CodeNow the component ships its own `.gitignore` - add any missing entries to
it rather than replacing it. Never commit secrets or a virtual environment.
