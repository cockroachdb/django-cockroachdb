# Changelog

## 3.1.2 - 2020-11-17

- Added support for CockroachDB 20.2.

- Fixed crash when cloning test databases: `TypeError: settings_to_cmd_args()
  missing 1 required positional argument: 'parameters'`.

- Fixed `dbshell` crash: `unknown flag: --password`.

- Prevented exception hiding in `DatabaseWrapper._nodb_cursor()`
  (`RuntimeError: generator didn't yield`).

- Fixed `dbshell` and `test` (if running tests in parallel) when using password
  authentication.

## 3.1.1 - 2020-10-14

- Fixed `dbshell` startup crash.

## 3.1 - 2020-08-05

Initial release for Django 3.1.x and CockroachDB 20.1.
