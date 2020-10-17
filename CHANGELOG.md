# Changelog

## 3.0.3 - Unreleased

- Fix `dbshell` crash: `unknown flag: --password`.

## 3.0.2 - 2020-08-05

- Enable `QuerySet.select_for_update()` and
  `QuerySet.select_for_update(of=...)` in CockroachDB 20.1.
- Fix creation/deletion of `unique_rowid()` default when altering to/from
  `AutoField`.

## 3.0.1 - 2020-05-20

- Add support for `QuerySet.explain()` options.
- Remove `psycopg2` from `setup.py`'s `install_requires` so that users can
  install either `psycopg2` or `psycopg2-binary`.
- Add support for CockroachDB 20.1.

## 3.0 - 2020-01-15

Initial release for Django 3.0.x and CockroachDB 19.2.
