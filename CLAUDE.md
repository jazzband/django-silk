# django-silky — Claude Code instructions

## Project overview

Fork of [django-silk](https://github.com/jazzband/django-silk) with a fully redesigned UI.
Published to PyPI as `django-silky`. GitHub: https://github.com/VaishnavGhenge/django-silky

Key differences from upstream:
- Light/dark theme toggle (CSS custom properties, localStorage persistence)
- Inline collapsible filter bar replacing the 300 px slide-out drawer
- Multi-column sort chips (session-persisted)
- Real Django `Paginator` replacing query slicing
- Hero bar + metric pill layout on all detail pages
- Self-hosted Lucide icons (no CDN calls)
- Sort + per-page reflected in URL for shareability

---

## Daily workflow

```bash
# Dev server (SQLite)
DB_ENGINE=sqlite3 .venv/bin/python project/manage.py runserver
# http://127.0.0.1:8000/silk/   (admin / admin)

# Watch SCSS (recompiles on every save)
npx gulp watch

# One-shot SCSS compile
npx gulp sass

# Run tests (expected: 277 passed, 1 skipped)
DB_ENGINE=sqlite3 .venv/bin/python -m pytest project/tests/ -q
```

---

## Where to edit the UI

| Layer | Location |
|---|---|
| HTML templates | `silk/templates/silk/` |
| SCSS source | `scss/` → compiled to `silk/static/silk/css/` |
| JS | `silk/static/silk/js/` |

### Key template files
- `silk/templates/silk/base/base.html` — root layout (theme toggle, Lucide init, nav)
- `silk/templates/silk/base/root_base.html` — pages with filter bar
- `silk/templates/silk/base/detail_base.html` — request/profile detail base
- `silk/templates/silk/requests.html` — main requests list
- `silk/templates/silk/summary.html` — dashboard
- `silk/templates/silk/profiling.html` — profiling list
- `silk/templates/silk/request.html` — request detail
- `silk/templates/silk/sql.html` — SQL query list
- `silk/templates/silk/sql_detail.html` — single SQL query
- `silk/templates/silk/profile_detail.html` — profile detail
- `silk/templates/silk/cprofile.html` — cProfile output
- `silk/templates/silk/clear_db.html` — clear database page

### Key SCSS files
- `scss/components/theme.scss` — all `--silk-*` CSS custom properties (light + dark)
- `scss/components/colors.scss` — performance colour variables
- `scss/pages/base.scss` — body, layout, `.silk-icon`, `.silk-badge`, `.silk-table`
- `scss/pages/requests.scss` — toolbar, filter bar, sort chips, pagination
- `scss/pages/request.scss` — hero bar, section cards, `.silk-detail-page`
- `scss/pages/summary.scss` — metric cards, top-N tables
- `scss/pages/root_base.scss` — nav, sidebar, drawer

### Key JS files
- `silk/static/silk/js/components/theme.js` — dark mode toggle + localStorage
- `silk/static/silk/js/pages/requests.js` — filter toggle, sort chips, URL state
- `silk/static/silk/js/pages/profiling.js` — filter toggle, URL state
- `silk/static/silk/js/pages/summary.js` — Lucide init
- `silk/static/silk/js/pages/request.js` — syntax highlight init
- `silk/static/silk/js/pages/profile_detail.js` — call-graph rendering

### Key Python files
- `silk/views/requests.py` — requests list view, multi-sort, pagination
- `silk/views/profiling.py` — profiling list view
- `silk/views/sql.py` — SQL query list view
- `silk/views/summary.py` — dashboard aggregates
- `silk/request_filters.py` — filter classes + `TIME_RANGE_PRESETS`
- `silk/templatetags/silk_filters.py` — template filters incl. `silk_full_datetime`, `silk_json`
- `silk/templatetags/silk_inclusion.py` — inclusion tags (menus, pagination)

---

## Architecture notes

### CSS variables
All colours are defined in `scss/components/theme.scss` as `--silk-*` custom properties.
Never use hardcoded hex values in SCSS — always use a variable.

Key tokens:
- `--silk-bg`, `--silk-surface`, `--silk-border` — backgrounds
- `--silk-text-primary`, `--silk-text-secondary`, `--silk-text-muted` — text
- `--silk-perf-very-good/good/ok/bad/very-bad` — 5-stop perf scale (green→red)
- `--silk-nav-bg`, `--silk-nav-text` — navigation bar

### State persistence
| State | Storage | Key |
|---|---|---|
| Theme | `localStorage` | `silk-theme` |
| Filter bar open (requests) | `localStorage` | `silk-filter-open` |
| Filter bar open (profiling) | `localStorage` | `silk-profiling-filter-open` |
| Active filters (requests) | Django session | `request_filters` |
| Sort order (requests) | Django session | `request_sort` |
| SQL per-page | Django session | `silk_sql_per_page` |
| Profiling per-page | Django session | `silk_profiling_show` |
| Sort + per-page (requests) | URL query params | `sort_criteria`, `per_page` |

### Sort chips
- Sort state is a JSON list: `[{"field": "start_time", "dir": "DESC"}, ...]`
- Stored in `request.session["request_sort"]`
- Submitted as hidden input `sort_criteria` via POST (JSON)
- The hidden input uses **single quotes** for the HTML attribute to avoid conflict with JSON double-quotes

### Icons
Lucide icons are self-hosted at `silk/static/silk/lib/lucide.min.js`.
Usage: `<i data-lucide="icon-name" class="silk-icon"></i>`.
`lucide.createIcons()` is called in every page's DOMContentLoaded handler.

---

## Building SCSS

The SCSS pipeline uses Dart Sass via gulp-sass 5.x (Node 24 compatible).

```bash
npx gulp watch    # watch mode
npx gulp sass     # one-shot
```

Config: `gulpfile.js`, `package.json`.

---

## Publishing to PyPI

**Releases are fully automated.** `.github/workflows/release.yml` triggers on any
`v[0-9]*` tag push, builds the distribution in CI, and publishes to PyPI via
**Trusted Publishing (OIDC)** — no API token, no `~/.pypirc`, no manual upload.

To ship a new version:

```bash
# 1. (Optional but recommended) Local dry-run build to catch packaging errors
#    BEFORE pushing the tag. This does NOT upload anything.
.venv/bin/python -m build
.venv/bin/twine check dist/*
rm dist/django_silky-*   # clean up so the locally-built artifacts don't linger

# 2. Tag and push — the push to origin is what triggers the release pipeline
git tag -a vX.Y.Z -m "vX.Y.Z — short summary"
git push origin master
git push origin vX.Y.Z
```

**Never run `twine upload` manually.** The CI pipeline races local uploads —
whichever finishes first claims the filename, and the loser gets a `400 File
already exists` because PyPI filename slots are immutable forever. If you see
that error, it almost certainly means CI already published successfully and the
manual upload was redundant.

Version numbers are derived from git tags by `setuptools_scm`, so the tag *is*
the source of truth — there's no `__version__` constant to bump anywhere.

Package metadata: `setup.py`
- Name: `django-silky`
- URL: `https://github.com/VaishnavGhenge/django-silky`
- Author / Maintainer: Vaishnav Ghenge (`vaishnavghenge@gmail.com`)
- Original `django-silk` attribution to Michael Ford / Jazzband lives in
  `README.md` and `LICENSE`, not in package metadata.

---

## Migration tooling

Users migrating from `django-silk` can use:
```bash
python migrate_to_silky.py --dry-run   # preview
python migrate_to_silky.py             # run migration
```

See `MIGRATING.md` for the full guide.

---

## Common fixes already applied

- `project/project/settings.py`: added `auth` + `messages` context processors required by Django admin
- `gulpfile.js` + `package.json`: migrated from node-sass (broken on Node 24) to Dart Sass
- `scss/pages/root_base.scss`: scoped `input` padding/width to `#cbp-spmenu-s2` to prevent CSS specificity overriding `.silk-filter-input`
- `silk/templates/silk/inclusion/sort_chips.html`: hidden input uses single-quoted attribute so embedded JSON doesn't truncate

---

## Test baseline

```
277 passed, 1 skipped
```

Run with: `DB_ENGINE=sqlite3 .venv/bin/python -m pytest project/tests/ -q`
