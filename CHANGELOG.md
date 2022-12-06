# Changelog

## 4.1.1 - 2022-12-06

- Made `dbshell` use `sslcert`, `sslkey`, `sslmode`, and `options` from the
  `'OPTIONS'` part of the `DATABASES` setting.
- Added support for CockroachDB 22.2, which adds support for
  `QuerySet.select_for_update(skip_locked=True)`.

## 4.1 - 2022-08-03

Initial release for Django 4.1.x and CockroachDB 21.2.x and 22.1.x.
