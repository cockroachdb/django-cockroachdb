# Changelog

## 6.1.1 - Unreleased

- Fixed `AlterField` operations that require a `USING` cast when a column's
  data type changes (e.g. `TextField` to `JSONField`). Such operations
  previously failed with an error like `column "<name>" cannot be cast
  automatically to type <type>`.

- Indexes are now created on all `ForeignKey`\s. Before CockroachDB v20.2, the
  database automatically created such indexes and this backend never adapted
  when that behavior changed.

  Indexes are not automatically added to existing tables. For example, this
  migration adds them for all foreign keys in an app (replace `myapp` with
  your app's label):

  ```python
  from django.db import migrations, models


  def add_foreign_key_indexes(apps, schema_editor):
      connection = schema_editor.connection
      with connection.cursor() as cursor:
          for model in apps.get_app_config("myapp").get_models():
              if not model._meta.managed:
                  continue
              constraints = connection.introspection.get_constraints(
                  cursor, model._meta.db_table
              )
              for field in model._meta.local_fields:
                  if not (field.remote_field and field.db_index and not field.unique):
                      continue
                  name = schema_editor._create_index_name(
                      model._meta.db_table, [field.column]
                  )
                  # Skip tables that already have the index (e.g. tables
                  # created by this version of the backend).
                  if name not in constraints:
                      schema_editor.add_index(
                          model, models.Index(fields=[field.name], name=name)
                      )


  class Migration(migrations.Migration):
      # CockroachDB can't run DDL statements inside a transaction.
      atomic = False
      dependencies = [("myapp", "0001_initial")]
      operations = [
          migrations.RunPython(add_foreign_key_indexes, migrations.RunPython.noop),
      ]
  ```

## 6.1 - 2026-08-07

Initial release for Django 6.1.x and CockroachDB 24.3.x, 25.2.x, 25.4.x,
26.2.x, and 26.3.x.
