from django.db.backends.postgresql.introspection import (
    DatabaseIntrospection as PostgresDatabaseIntrospection,
)


class DatabaseIntrospection(PostgresDatabaseIntrospection):
    data_types_reverse = dict(PostgresDatabaseIntrospection.data_types_reverse)
    data_types_reverse[1184] = 'DateTimeField'  # TIMESTAMPTZ
    index_default_access_method = 'prefix'

    def get_constraints(self, cursor, table_name):
        constraints = super().get_constraints(cursor, table_name)
        # CockroachDB synthesizes a row in pg_constraint with contype='n' for
        # each NOT NULL column (PG18-compatible behavior). Django's postgres
        # backend gained a "contype != 'n'" filter during 6.1 development
        # (django/django#19910) but no released version has it yet.
        cursor.execute(
            """
            SELECT c.conname
            FROM pg_constraint AS c
            JOIN pg_class AS cl ON c.conrelid = cl.oid
            WHERE cl.relname = %s
                AND pg_catalog.pg_table_is_visible(cl.oid)
                AND c.contype = 'n'
            """,
            [table_name],
        )
        for (name,) in cursor.fetchall():
            constraints.pop(name, None)
        return constraints
