# Alembic is legacy here — do not run `alembic upgrade`

These migrations come from an earlier phase (UUID ids, tables later rebuilt). The schema is now owned by
`database/Model/*.json` → `php setup.php` (see `skills/SKILL.md`), and production changes ship as
additive SQL in `database/migrations/` (e.g. `2026-09-26-cloudsql-additive.sql`).
Running these scripts can clash with the generated schema. They are kept for reference only.
