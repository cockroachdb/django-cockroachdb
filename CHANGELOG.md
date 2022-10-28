# Changelog

## 3.2.4 - Unreleased

- Confirmed support for CockroachDB 22.1.x. No code changes were required.
- Made `dbshell` use `sslcert`, `sslkey`, `sslmode`, and `options` from the
  `'OPTIONS'` part of the `DATABASES` setting.

## 3.2.3 - 2022-04-14

- Added support for 3D geometries.
- Added validation of `QuerySet.explain()` options.

## 3.2.2 - 2021-11-16

- Added support for CockroachDB 21.2.x.

## 3.2.1 - 2021-05-20

- Added support for CockroachDB 21.1.x.

## 3.2 - 2021-04-08

Initial release for Django 3.2.x and CockroachDB 20.2.
