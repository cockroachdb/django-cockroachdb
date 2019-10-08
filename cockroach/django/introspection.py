from django.db.backends.base.introspection import TableInfo
from django.db.backends.postgresql.introspection import (
    DatabaseIntrospection as PostgresDatabaseIntrospection,
)


class DatabaseIntrospection(PostgresDatabaseIntrospection):
    data_types_reverse = dict(PostgresDatabaseIntrospection.data_types_reverse)
    data_types_reverse[1184] = 'DateTimeField'  # TIMESTAMPZ

    def get_table_list(self, cursor):
        cursor.execute("SHOW TABLES")
        # The second TableInfo field is 't' for table or 'v' for view.
        return [TableInfo(row[0], 't') for row in cursor.fetchall()]
