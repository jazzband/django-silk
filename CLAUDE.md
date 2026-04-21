# django-silky — Claude Code instructions

## Commit rules
- Never mention claude as co-author in commit messages.
- Follow [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/).

### Format
```
<type>[optional scope][!]: <description>

[optional body]

[optional footer(s)]
```

### Types
- `feat`: new feature (correlates with MINOR in SemVer)
- `fix`: bug fix (correlates with PATCH in SemVer)
- `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`

### Breaking changes
- Append `!` after type/scope **or** add a `BREAKING CHANGE:` footer (either triggers a MAJOR bump).
- Example: `feat(api)!: drop support for Python 3.8`

### Rules
- Description is lowercase, imperative mood, no trailing period, ≤72 chars.
- Scope is optional and in parentheses: `fix(parser): ...`.
- Body (if present) is separated from description by a blank line and explains the *why*, not the *what*.
- Footers use `Token: value` form (e.g., `Refs: #123`, `BREAKING CHANGE: ...`).

### Examples
- `feat(ui): add dark mode toggle to request detail page`
- `fix: handle empty querysets in profile aggregation`
- `refactor!: rename SilkyConfig.SILKY_AUTHENTICATE to SILKY_REQUIRE_AUTH`
- `docs(readme): document DB_ENGINE env var for local dev`


## Execution
- Run tests with: `DB_ENGINE=sqlite3 .venv/bin/python -m pytest project/tests/ -q`
- Run demo project with: `DB_ENGINE=sqlite3 .venv/bin/python project/manage.py runserver`
