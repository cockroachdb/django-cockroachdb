from django.db.backends.base.schema import BaseDatabaseSchemaEditor
from django.db.backends.postgresql.schema import (
    DatabaseSchemaEditor as PostgresDatabaseSchemaEditor,
)


class DatabaseSchemaEditor(PostgresDatabaseSchemaEditor):
    # Partial indexes ('%(condition)s' in SQL string) aren't implemented in
    # cockroachdb: https://github.com/cockroachdb/cockroach/issues/9683
    # If implemented, this attribute can be removed.
    sql_create_index = 'CREATE INDEX %(name)s ON %(table)s%(using)s (%(columns)s)%(extra)s'

    # The PostgreSQL backend uses "SET CONSTRAINTS ... IMMEDIATE" before
    # "ALTER TABLE..." to run any any deferred checks to allow dropping the
    # foreign key in the same transaction. This doesn't apply to cockroachdb.
    sql_delete_fk = "ALTER TABLE %(table)s DROP CONSTRAINT %(name)s"

    def _index_columns(self, table, columns, col_suffixes, opclasses):
        # cockroachdb doesn't support PostgreSQL opclasses.
        return BaseDatabaseSchemaEditor._index_columns(self, table, columns, col_suffixes, opclasses)

    def _create_like_index_sql(self, model, field):
        # cockroachdb doesn't support LIKE indexes.
        return None

    def _alter_field(self, model, old_field, new_field, old_type, new_type,
                     old_db_params, new_db_params, strict=False):
        # Skip to the base class to avoid trying to add or drop
        # PostgreSQL-specific LIKE indexes.
        BaseDatabaseSchemaEditor._alter_field(
            self, model, old_field, new_field, old_type, new_type, old_db_params,
            new_db_params, strict,
        )
