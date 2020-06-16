# Changelog

## 2.2.3 - Unreleased

- Fix `dbshell` crash: `unknown flag: --password`.
- Add support for CockroachDB 20.2.

## 2.2.2 - 2020-08-05

- Enable `QuerySet.select_for_update()` and
  `QuerySet.select_for_update(of=...)` in CockroachDB 20.1.
- Fix creation/deletion of `unique_rowid()` default when altering to/from
  `AutoField`.

## 2.2.1 - 2020-05-15

- Add support for `QuerySet.explain()` options.
- Remove `psycopg2` from `setup.py`'s `install_requires` so that users can
  install either `psycopg2` or `psycopg2-binary`.
- Add support for CockroachDB 20.1.

## 2.2 - 2020-01-15

Initial release for Django 2.2.x and CockroachDB 19.2.
