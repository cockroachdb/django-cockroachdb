from django.db.backends.postgresql.introspection import (
    DatabaseIntrospection as PostgresDatabaseIntrospection,
)


class DatabaseIntrospection(PostgresDatabaseIntrospection):
    data_types_reverse = dict(PostgresDatabaseIntrospection.data_types_reverse)
    data_types_reverse[1184] = 'DateTimeField'  # TIMESTAMPTZ
    index_default_access_method = 'prefix'
