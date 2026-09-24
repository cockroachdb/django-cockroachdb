import re

from django.db.backends.base.schema import BaseDatabaseSchemaEditor
from django.db.backends.postgresql.schema import (
    DatabaseSchemaEditor as PostgresDatabaseSchemaEditor,
)
from django.db.backends.utils import strip_quotes


class DatabaseSchemaEditor(PostgresDatabaseSchemaEditor):
    # The PostgreSQL backend uses "SET CONSTRAINTS ... IMMEDIATE" before
    # "ALTER TABLE..." to run any deferred checks to allow dropping the foreign
    # key in the same transaction. This doesn't apply to CockroachDB.
    sql_delete_fk = "ALTER TABLE %(table)s DROP CONSTRAINT %(name)s"

    # "ALTER TABLE ... DROP CONSTRAINT ..." not supported for dropping UNIQUE
    # constraints; must use this instead.
    sql_delete_unique = "DROP INDEX %(name)s CASCADE"

    # The PostgreSQL backend uses "SET CONSTRAINTS ... IMMEDIATE" after
    # creating this foreign key. This isn't supported by CockroachDB.
    sql_create_column_inline_fk = (
        'CONSTRAINT %(name)s REFERENCES %(to_table)s(%(to_column)s)'
        '%(on_delete_db)s%(deferrable)s'
    )

    # The PostgreSQL backend uses "SET CONSTRAINTS ... IMMEDIATE" after this
    # statement. This isn't supported by CockroachDB.
    sql_update_with_default = "UPDATE %(table)s SET %(column)s = %(default)s WHERE %(column)s IS NULL"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # (table, column) pairs of foreign key indexes created by table_sql().
        self._inlined_fk_indexes = set()

    def __enter__(self):
        super().__enter__()
        # As long as DatabaseFeatures.can_rollback_ddl = False, compose() may
        # fail if connection is None as per
        # https://github.com/django/django/pull/15687#discussion_r1038175823.
        # See also https://github.com/django/django/pull/15687#discussion_r1041503991.
        self.connection.ensure_connection()
        return self

    def table_sql(self, model):
        sql, params = super().table_sql(model)
        # Create indexes on foreign keys as part of CREATE TABLE rather than in
        # separate CREATE INDEX statements. Every DDL statement has a fixed
        # overhead on CockroachDB (a schema change job and descriptor version
        # changes). The foreign key constraints themselves must remain
        # deferred because the referenced table may not exist yet.
        index_sqls = []
        for field in model._meta.local_fields:
            if field.remote_field and self._field_should_be_indexed(model, field):
                index_name = self._create_index_name(model._meta.db_table, [field.column])
                index_sqls.append('INDEX %s (%s)' % (
                    self.quote_name(index_name),
                    self.quote_name(field.column),
                ))
                self._inlined_fk_indexes.add((model._meta.db_table, field.column))
        if index_sqls:
            end = sql.rindex(')')
            sql = '%s, %s%s' % (sql[:end], ', '.join(index_sqls), sql[end:])
        return sql, params

    def _field_indexes_sql(self, model, field):
        # Skip indexes that table_sql() already created.
        key = (model._meta.db_table, field.column)
        if key in self._inlined_fk_indexes:
            # Only skip once so that a later call for the same column (e.g.
            # remove_field() followed by add_field()) still creates the index.
            self._inlined_fk_indexes.remove(key)
            return []
        return super()._field_indexes_sql(model, field)

    def add_index(self, model, index, concurrently=False):
        if index.contains_expressions and not self.connection.features.supports_expression_indexes:
            return None
        super().add_index(model, index, concurrently)

    def remove_index(self, model, index, concurrently=False):
        if index.contains_expressions and not self.connection.features.supports_expression_indexes:
            return None
        super().remove_index(model, index, concurrently)

    def _index_columns(self, table, columns, col_suffixes, opclasses):
        # CockroachDB doesn't support PostgreSQL opclasses.
        return BaseDatabaseSchemaEditor._index_columns(self, table, columns, col_suffixes, opclasses)

    def _create_like_index_sql(self, model, field):
        # CockroachDB doesn't support LIKE indexes.
        return None

    def _alter_field(self, model, old_field, new_field, old_type, new_type,
                     old_db_params, new_db_params, strict=False):
        # ALTER COLUMN TYPE is experimental.
        # https://github.com/cockroachdb/cockroach/issues/49329
        if (
            not self.connection.features.is_cockroachdb_25_1 and (
                old_type != new_type or
                getattr(old_field, 'db_collation', None) != getattr(new_field, 'db_collation', None)
            )
        ):
            self.execute('SET enable_experimental_alter_column_type_general = true')
        # Skip to the base class to avoid trying to add or drop
        # PostgreSQL-specific LIKE indexes.
        BaseDatabaseSchemaEditor._alter_field(
            self, model, old_field, new_field, old_type, new_type, old_db_params,
            new_db_params, strict,
        )
        # Add or remove `DEFAULT unique_rowid()` for AutoField.
        old_suffix = old_field.db_type_suffix(self.connection)
        new_suffix = new_field.db_type_suffix(self.connection)
        if old_suffix != new_suffix:
            if new_suffix:
                self.execute(self.sql_alter_column % {
                    'table': self.quote_name(model._meta.db_table),
                    'changes': 'ALTER COLUMN %(column)s SET %(expression)s' % {
                        'column': self.quote_name(new_field.column),
                        'expression': new_suffix,
                    }
                })
            else:
                self.execute(self.sql_alter_column % {
                    'table': self.quote_name(model._meta.db_table),
                    'changes': 'ALTER COLUMN %(column)s DROP DEFAULT' % {
                        'column': self.quote_name(new_field.column),
                    }
                })

    def _alter_column_type_sql(self, model, old_field, new_field, new_type, old_collation, new_collation):
        self.sql_alter_column_type = (
            "ALTER COLUMN %(column)s TYPE %(type)s%(collation)s"
        )
        # Cast when data type changed.
        if using_sql := self._using_sql(new_field, old_field):
            # The USING expression must include the collation.
            if collate_sql := self._collate_sql(
                new_collation, old_collation, model._meta.db_table
            ):
                using_sql += f" {collate_sql}"
            self.sql_alter_column_type += using_sql
        new_internal_type = new_field.get_internal_type()
        old_internal_type = old_field.get_internal_type()
        # Make ALTER TYPE with AutoField make sense.
        auto_field_types = {'AutoField', 'BigAutoField', 'SmallAutoField'}
        old_is_auto = old_internal_type in auto_field_types
        new_is_auto = new_internal_type in auto_field_types
        if new_is_auto and not old_is_auto:
            column = strip_quotes(new_field.column)
            return (
                (
                    self.sql_alter_column_type % {
                        "column": self.quote_name(column),
                        "type": new_type,
                        "collation": "",
                    },
                    [],
                ),
                # The PostgreSQL backend manages the column's identity here but
                # this isn't applicable on CockroachDB because unique_rowid()
                # is used instead.
                [],
            )
        else:
            return BaseDatabaseSchemaEditor._alter_column_type_sql(
                self, model, old_field, new_field, new_type,
                old_collation, new_collation,
            )

    # AutoField and IntegerField variants (and foreign keys to any of them) are
    # all stored as the same 64-bit integer type, so a change between them
    # doesn't require a cast. Adding a USING clause anyway makes CockroachDB
    # treat the change as one that requires rewriting on-disk data, which fails
    # for columns that are part of an index.
    integer_db_types = {'integer', 'bigint', 'smallint'}

    def _using_sql(self, new_field, old_field):
        old_db_type = self._field_data_type(old_field)
        new_db_type = self._field_data_type(new_field)
        if (
            old_db_type in self.integer_db_types
            and new_db_type in self.integer_db_types
        ):
            return ""
        # A change that only affects a type's parameters (e.g. varchar(5) to
        # varchar(11)) doesn't require a cast either, and forcing one causes
        # the same on-disk data rewrite problem as above.
        if self._strip_type_params(old_db_type) == self._strip_type_params(new_db_type):
            return ""
        return super()._using_sql(new_field, old_field)

    def _strip_type_params(self, db_type):
        # _field_data_type() can return a callable (e.g. for CharField and
        # DecimalField) rather than a resolved type string, in which case
        # there are no parameters to strip.
        if not isinstance(db_type, str):
            return db_type
        # Remove the suffix from the datatype, e.g. 'varchar(#)' -> 'varchar'.
        return re.sub(r'\(.*\)', '', db_type)
