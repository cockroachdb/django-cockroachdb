# CockroachDB backend for Django

## Install and usage

Use the version of django-cockroachdb that corresponds to your version of
Django. For example, to get the latest compatible release for Django 3.0.x:

`pip install django-cockroachdb==3.0.*`

The minor release number of Django doesn't correspond to the minor release
number of django-cockroachdb. Use the latest minor release of each.

If a release series of django-cockroachdb only has pre-releases (alphas or
betas), you'll see an error with a list of the available versions. In that
case, specify the exact version that you want. For example, if
django-cockroachdb 3.0 alpha 1 is available:

```
$ pip install django-cockroachdb==3.0.*`
ERROR: Could not find a version that satisfies the requirement
django-cockroachdb==3.0.* (from versions: 3.0a1)

$ pip install django-cockroachdb==3.0a1
...
Successfully installed django-cockroachdb-3.0a1 psycopg2-2.8.4
```

Configure the Django `DATABASES` setting similar to this:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django_cockroachdb',
        'NAME': 'django',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '26257',
        # If connecting with SSL, remove the PASSWORD entry above and include
        # the section below, replacing the file paths as appropriate.
        'OPTIONS': {
            'sslmode': 'require',
            'sslrootcert': '/certs/ca.crt',
            'sslcert': '/certs/client.myprojectuser.crt',
            'sslkey': '/certs/client.myprojectuser.key',
        },
    },
}
```

## Notes on Django fields

1. `CharField`'s `max_length` is ignored. It uses the same storage as
   `TextField` so `CharField` is introspected by `inspectdb` as `TextField`.

2. `IntegerField` uses the same storage as `BigIntegerField` so `IntegerField`
   is introspected by `inspectdb` as `BigIntegerField`.

3. `AutoField` and `BigAutoField` are both stored as
   [integer](https://www.cockroachlabs.com/docs/stable/int.html) (64-bit) with
   [`DEFAULT unique_rowid()`](https://www.cockroachlabs.com/docs/stable/functions-and-operators.html#id-generation-functions).

## FAQ

### Why do I get the error ``psycopg2.errors.InvalidName: no database specified``?

You may need to [create the database](https://www.cockroachlabs.com/docs/stable/create-database.html).
You can use `cockroach sql --insecure` on the command line to get a SQL prompt.

## Known issues and limitations (as of cockroachdb 19.2.2)

1. CockroachDB [doesn't support savepoints](https://github.com/cockroachdb/cockroach/issues/10735).
   This means a few things:

   1. Django's [transaction.atomic()](https://docs.djangoproject.com/en/stable/topics/db/transactions/#django.db.transaction.atomic)
      can't be nested.
   2. Django's `TestCase` works like `TransactionTestCase`. That is,
      transactions aren't used to speed up the former.

2. CockroachDB [can't disable constraint checking](https://github.com/cockroachdb/cockroach/issues/19444),
   which means certain things in Django like forward references in fixtures
   aren't supported.

4. Migrations have some limitations. CockroachDB doesn't support:

   1. [changing column type](https://github.com/cockroachdb/cockroach/issues/9851)
   2. dropping or changing a table's primary key

5. Known Bugs:
   1. [The extract() function doesn't respect the time zone.](https://github.com/cockroachdb/django-cockroachdb/issues/47)
   2. [Interval math across daylight saving time is incorrect.](https://github.com/cockroachdb/django-cockroachdb/issues/54)
   3. [`date_trunc('week', <value>)` truncates to midnight Sunday rather than Monday](https://github.com/cockroachdb/django-cockroachdb/issues/92)
   4. [date_trunc() results are incorrectly localized.](https://github.com/cockroachdb/django-cockroachdb/issues/32)
   5. [cast() timestamptz to time doesn't respect the time zone.](https://github.com/cockroachdb/django-cockroachdb/issues/37)
   6. [Interval math may be incorrect on date columns.](https://github.com/cockroachdb/django-cockroachdb/issues/53)

6. Unsupported queries:
   1. [Mixed type addition in SELECT](https://github.com/cockroachdb/django-cockroachdb/issues/19):
      `unsupported binary operator: <int> + <float>`
   2. [UPDATE float column with integer column](https://github.com/cockroachdb/django-cockroachdb/issues/20):
      `value type int doesn't match type FLOAT8 of column <name>`
   3. [Division that yields a different type](https://github.com/cockroachdb/django-cockroachdb/issues/21):
      `unsupported binary operator: <int> / <int> (desired <int>)`
   4. [The power() database function doesn't accept negative exponents](https://github.com/cockroachdb/django-cockroachdb/issues/22):
      `power(): integer out of range`
   5. The `StdDev` and `Variance` aggregates
      [aren't supported](https://github.com/cockroachdb/django-cockroachdb/issues/25).
   6. [extract() doesn't support interval columns (DurationField)](https://github.com/cockroachdb/django-cockroachdb/issues/29):
      `unknown signature: extract(string, interval)`
   7. [The log() function doesn't support custom bases](https://github.com/cockroachdb/django-cockroachdb/issues/50):
      `unknown signature: extract(string, interval)`
   8. [sum() doesn't support arguments of different types](https://github.com/cockroachdb/django-cockroachdb/issues/73):
      `sum(): unsupported binary operator: <float> + <int>`
   9. [greatest() doesn't support arguments of different types](https://github.com/cockroachdb/django-cockroachdb/issues/74):
      `greatest(): expected <arg> to be of type <type>, found type <other type>`
   10. The [isoyear lookup](https://github.com/cockroachdb/django-cockroachdb/issues/28) isn't supported:
       `extract(): unsupported timespan: isoyear`
   11. [timezone() doesn't support UTC offsets](https://github.com/cockroachdb/django-cockroachdb/issues/97):
       `timezone(): unknown time zone UTC...`
   12. [`SmallAutoField` generates values that are too large for any corresponding foreign keys](https://github.com/cockroachdb/django-cockroachdb/issues/84).
   13. [The `SHA224` and `SHA384` database functions aren't supported](https://github.com/cockroachdb/django-cockroachdb/issues/81).
