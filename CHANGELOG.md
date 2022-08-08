# Changelog

## 4.0.2 - Unreleased

- Confirmed support for CockroachDB 22.1.x. No code changes were required.
- Made `dbshell` use `sslmode` and `options` from the `'OPTIONS'` part of the
  `DATABASES` setting.
- Made `dbshell` use `sslcert`, `sslkey`, `sslmode`, and `options` from the
  `'OPTIONS'` part of the `DATABASES` setting.
- Added support for CockroachDB 22.2, which adds support for
  `QuerySet.select_for_update(skip_locked=True)`.

## 4.0.1 - 2022-04-14

- Added validation of `QuerySet.explain()` options.

## 4.0 - 2022-01-20

Initial release for Django 4.0.x and CockroachDB 21.1.x and 21.2.x.
