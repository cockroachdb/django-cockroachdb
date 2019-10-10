from django.db.backends.base.schema import BaseDatabaseSchemaEditor
from django.db.backends.postgresql.schema import (
    DatabaseSchemaEditor as PostgresDatabaseSchemaEditor,
)


class DatabaseSchemaEditor(PostgresDatabaseSchemaEditor):
    # Partial indexes ('%(condition)s' in SQL string) aren't implemented in
    # cockroachdb: https://github.com/cockroachdb/cockroach/issues/9683
    # If implemented, this attribute can be removed.
    sql_create_index = 'CREATE INDEX %(name)s ON %(table)s%(using)s (%(columns)s)%(extra)s'

    def _index_columns(self, table, columns, col_suffixes, opclasses):
        # cockroachdb doesn't support PostgreSQL opclasses.
        return BaseDatabaseSchemaEditor._index_columns(self, table, columns, col_suffixes, opclasses)

    def _model_indexes_sql(self, model):
        # Postgres customizes _model_indexes_sql to add special-case
        # options for string fields. Skip to the base class version
        # to avoid this.
        return BaseDatabaseSchemaEditor._model_indexes_sql(self, model)

    def _field_indexes_sql(self, model, field):
        # Postgres needs an operator defined for like queries to work
        # properly text and varchars. Skip to the base class version
        # to avoid this.
        return BaseDatabaseSchemaEditor._field_indexes_sql(self, model, field)

    def _alter_field(self, model, old_field, new_field, old_type, new_type,
                     old_db_params, new_db_params, strict=False):

        if old_field.db_index or old_field.unique:
            index_name = self._create_index_name(model._meta.db_table, [old_field.column])
            self.execute(self._delete_index_sql(model, index_name))

        BaseDatabaseSchemaEditor._alter_field(
            self, model, old_field, new_field, old_type, new_type, old_db_params,
            new_db_params, strict,
        )
