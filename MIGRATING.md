# Migrating from django-silk to django-silky

## Upgrading to django-silky 1.2.0 — defaults are now secure

**What changed.** In earlier releases `SILKY_AUTHENTICATION` and `SILKY_AUTHORISATION` both defaulted to `False`, so anyone with network access to `/silk/` could read the full profiling UI. Starting with 1.2.0 both default to `True`, and the default `SILKY_PERMISSIONS` predicate requires `user.is_staff`.

**Who is affected.** Anyone who was relying on the unauthenticated `/silk/` UI — whether intentionally (internal dev server, air-gapped environment) or not.

**Symptom after upgrade.** Visiting `/silk/` as an anonymous user, or as a logged-in non-staff user, now returns `404 Not Found`. Logged-in staff users see the UI unchanged.

**Opting back in to the old behaviour.** Add to `settings.py`:

```python
SILKY_AUTHENTICATION = False
SILKY_AUTHORISATION = False
```

**Why 404 and not 403?** To reduce fingerprinting — a 404 doesn't reveal that silk is mounted. This is defense-in-depth; the real security is the auth check itself.

**Caveat: static-asset fingerprinting.** Static files under `/static/silk/…` are served by your static-file stack (nginx, whitenoise, etc.) and are not covered by silk's auth decorators. If you need full opacity, restrict that prefix at your edge.

---

## From django-silk to django-silky

`django-silky` is a **drop-in replacement** for `django-silk`. It uses the
same Django app label (`silk`), the same database schema, and the same
migrations (0001 – 0008). Switching does **not** drop, alter, or move any
existing tables — all recorded requests, SQL queries, and profiles are
retained.

---

## Compatibility matrix

| django-silk version | Compatible with django-silky? | Notes |
|---|---|---|
| 5.4.x (latest) | ✅ Yes — direct swap | No migration needed |
| 5.3.x | ✅ Yes | No migration needed |
| 5.0 – 5.2 | ✅ Yes | No migration needed |
| < 5.0 | ⚠️ Upgrade first | Run upstream migrations to 0008 before switching |

> **Baseline:** `django-silky` is forked from `django-silk` master
> (post-5.4.3, commit `2db6175`). The database schema is identical.

---

## Migration steps

### From django-silk 5.x (recommended path)

1. **Back up your database** (always a good idea before swapping packages):

   ```bash
   # PostgreSQL
   pg_dump -Fc mydb > silk_backup_$(date +%Y%m%d).dump

   # MySQL
   mysqldump mydb > silk_backup_$(date +%Y%m%d).sql

   # SQLite
   cp db.sqlite3 db.sqlite3.bak
   ```

2. **Swap the package** — uninstall the old, install the new:

   ```bash
   pip uninstall django-silk
   pip install django-silky
   ```

3. **No `migrate` needed.** The schema is identical. Confirm the migration
   state is clean:

   ```bash
   python manage.py showmigrations silk
   ```

   Expected output:

   ```
   silk
    [X] 0001_initial
    [X] 0002_auto_update_uuid4_id_field
    [X] 0003_request_prof_file
    [X] 0004_request_prof_file_storage
    [X] 0005_increase_request_prof_file_length
    [X] 0006_fix_request_prof_file_blank
    [X] 0007_sqlquery_identifier
    [X] 0008_sqlquery_analysis
   ```

   All 8 migrations should already be checked off — they were applied when
   you were running django-silk, and the files are identical.

4. **No `settings.py` changes.** The app label stays `'silk'`:

   ```python
   # unchanged — this is correct for django-silky too
   INSTALLED_APPS = [
       ...
       'silk',
   ]
   ```

5. **Restart your server** and visit `/silk/` to verify the UI loads and
   your existing data is visible.

---

### From django-silk < 5.0

You must first bring the upstream migrations up to `0008` before switching.

1. While still on django-silk, run all pending migrations:

   ```bash
   pip install "django-silk>=5.4"
   python manage.py migrate silk
   ```

2. Confirm all 8 migrations are applied (`showmigrations silk` shows all `[X]`).

3. Then follow the **From django-silk 5.x** steps above.

---

## What changes in the UI

The underlying data model is unchanged. The only differences are visual:

- **Requests page** — sortable chips, inline filter bar, paginator, method/status badges
- **Summary page** — metric cards, time-range presets, top-N tables
- **Request detail** — hero bar with metric pills, section cards
- **SQL / Profiling** — same data, modernized layout
- **Dark mode** — toggle in the nav bar, preference saved in `localStorage`

All configuration settings (`SILKY_*`) continue to work exactly as before.

---

## Rollback

If you need to revert to `django-silk`:

```bash
pip uninstall django-silky
pip install django-silk
```

No data migration or `manage.py migrate` is required in either direction —
the schema is shared.

---

## Verifying data retention

After switching, spot-check a few things in the `/silk/` UI:

- [ ] Requests table shows historical entries with correct timestamps
- [ ] Clicking a request opens its detail page (headers, body, SQL count)
- [ ] SQL tab lists queries for an existing request
- [ ] Profiling page shows any previously recorded profiles
- [ ] Summary page shows aggregate metrics from historical data

If any page raises a `ProgrammingError` or `OperationalError`, run
`python manage.py showmigrations silk` — if any migration shows `[ ]`
(unapplied), run `python manage.py migrate silk` to apply it.

---

## Frequently asked questions

**Does django-silky add new migrations?**
Not at this time. If future schema changes are needed they will be added as
new numbered migrations (0009, 0010, …) in the standard Django way, and a
note will appear here.

**Can I use django-silky and django-silk at the same time?**
No — both install under the `silk` app label, so only one can be installed
in a given Python environment.

**Will my `SILKY_*` settings still work?**
Yes, all configuration options are unchanged. See the
[Configuration section in the README](README.md#configuration) for the full
list.
