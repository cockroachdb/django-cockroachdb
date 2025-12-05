# Changelog

## 5.2.1 - 2025-12-04

- Confirmed support for CockroachDB 25.2.x, 25.3.x, and 25.4.x (no code changes
  required).
- Fixed the ``Now`` database function to use the statement time
  (``STATEMENT_TIMESTAMP``) rather than the transaction time
  (``CURRENT_TIMESTAMP``).

## 5.2 - 2025-04-07

Initial release for Django 5.2.x and CockroachDB 23.2.x, 24.1.x, 24.3.x, and
25.1.x.
