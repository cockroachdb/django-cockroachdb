from django.db.backends.postgresql.base import (
    DatabaseWrapper as PostgresDatabaseWrapper,
)
from django.db.utils import IntegrityError

from .client import DatabaseClient
from .creation import DatabaseCreation
from .features import DatabaseFeatures
from .introspection import DatabaseIntrospection
from .operations import DatabaseOperations
from .schema import DatabaseSchemaEditor


class DatabaseWrapper(PostgresDatabaseWrapper):
    vendor = 'cockroachdb'

    # Override some types from the postgresql adapter.
    data_types = dict(
        PostgresDatabaseWrapper.data_types,
        AutoField='integer',
        DateTimeField='timestamptz',
    )
    data_types_suffix = dict(
        PostgresDatabaseWrapper.data_types_suffix,
        AutoField='DEFAULT unique_rowid()',
    )

    SchemaEditorClass = DatabaseSchemaEditor
    creation_class = DatabaseCreation
    features_class = DatabaseFeatures
    introspection_class = DatabaseIntrospection
    ops_class = DatabaseOperations
    client_class = DatabaseClient

    def check_constraints(self, table_names=None):
        # Cribbed from django.db.backends.mysql.operations
        """
        Check each table name in `table_names` for rows with invalid foreign
        key references. This method is intended to be used in conjunction with
        `disable_constraint_checking()` and `enable_constraint_checking()`, to
        determine if rows with invalid references were entered while constraint
        checks were off.
        """
        with self.cursor() as cursor:
            if table_names is None:
                table_names = self.introspection.table_names(cursor)
            for table_name in table_names:
                primary_key_column_name = self.introspection.get_primary_key_column(cursor, table_name)
                if not primary_key_column_name:
                    continue
                key_columns = self.introspection.get_key_columns(cursor, table_name)
                for column_name, referenced_table_name, referenced_column_name in key_columns:
                    cursor.execute(
                        """
                        SELECT REFERRING.`%s`, REFERRING.`%s` FROM `%s` as REFERRING
                        LEFT JOIN `%s` as REFERRED
                        ON (REFERRING.`%s` = REFERRED.`%s`)
                        WHERE REFERRING.`%s` IS NOT NULL AND REFERRED.`%s` IS NULL
                        """ % (
                            primary_key_column_name, column_name, table_name,
                            referenced_table_name, column_name, referenced_column_name,
                            column_name, referenced_column_name,
                        )
                    )
                    for bad_row in cursor.fetchall():
                        raise IntegrityError(
                            "The row in table '%s' with primary key '%s' has an invalid "
                            "foreign key: %s.%s contains a value '%s' that does not "
                            "have a corresponding value in %s.%s."
                            % (
                                table_name, bad_row[0], table_name, column_name,
                                bad_row[1], referenced_table_name, referenced_column_name,
                            )
                        )

    def chunked_cursor(self):
        return self.cursor()

    def _set_autocommit(self, autocommit):
        with self.wrap_database_errors:
            self.connection.autocommit = autocommit
