from django.db.backends.base.introspection import TableInfo
from django.db.backends.postgresql.introspection import (
    DatabaseIntrospection as PostgresDatabaseIntrospection,
)
from django.db.models import Index


class DatabaseIntrospection(PostgresDatabaseIntrospection):
    data_types_reverse = dict(PostgresDatabaseIntrospection.data_types_reverse)
    data_types_reverse[1184] = 'DateTimeField'  # TIMESTAMPTZ

    def get_table_list(self, cursor):
        if not self.connection.features.is_cockroachdb_20_2:
            # `type` isn't included in SHOW TABLES.
            cursor.execute("SELECT table_name FROM [SHOW TABLES]")
            return [TableInfo(row[0], 't') for row in cursor.fetchall()]

        cursor.execute("SELECT table_name, type FROM [SHOW TABLES]")
        # The second TableInfo field is 't' for table or 'v' for view.
        return [TableInfo(row[0], 't' if row[1] == 'table' else 'v') for row in cursor.fetchall()]

    def get_constraints(self, cursor, table_name):
        """
        Retrieve any constraints or keys (unique, pk, fk, check, index) across
        one or more columns. Also retrieve the definition of expression-based
        indexes.

        This comes from Django before 1d8cfa36089f2d1295abad03a99fc3c259bde6b5
        where unnest(anyarray, anyarray) usage was added. Remove this method
        when cockroachdb supports unnest(anyarray, anyarray):
        https://github.com/cockroachdb/cockroach/issues/41434
        """
        constraints = {}
        # Loop over the key table, collecting things as constraints. The column
        # array must return column names in the same order in which they were
        # created.
        cursor.execute("""
            SELECT
                c.conname,
                array(
                    SELECT attname
                    FROM (
                        SELECT unnest(c.conkey) AS colid,
                               generate_series(1, array_length(c.conkey, 1)) AS arridx
                    ) AS cols
                    JOIN pg_attribute AS ca ON cols.colid = ca.attnum
                    WHERE ca.attrelid = c.conrelid
                    ORDER BY cols.arridx
                ),
                c.contype,
                (SELECT fkc.relname || '.' || fka.attname
                FROM pg_attribute AS fka
                JOIN pg_class AS fkc ON fka.attrelid = fkc.oid
                WHERE fka.attrelid = c.confrelid AND fka.attnum = c.confkey[1]),
                cl.reloptions
            FROM pg_constraint AS c
            JOIN pg_class AS cl ON c.conrelid = cl.oid
            JOIN pg_namespace AS ns ON cl.relnamespace = ns.oid
            WHERE ns.nspname = %s AND cl.relname = %s
        """, ["public", table_name])
        for constraint, columns, kind, used_cols, options in cursor.fetchall():
            constraints[constraint] = {
                "columns": columns,
                "primary_key": kind == "p",
                "unique": kind in ["p", "u"],
                "foreign_key": tuple(used_cols.split(".", 1)) if kind == "f" else None,
                "check": kind == "c",
                "index": False,
                "definition": None,
                "options": options,
            }
        # Now get indexes
        cursor.execute("""
            SELECT
                indexname, array_agg(attname ORDER BY rnum), indisunique, indisprimary,
                array_agg(ordering ORDER BY rnum), amname, exprdef, s2.attoptions
            FROM (
                SELECT
                    c2.relname as indexname, idx.*, attr.attname, am.amname,
                    CASE
                        WHEN idx.indexprs IS NOT NULL THEN
                            pg_get_indexdef(idx.indexrelid)
                    END AS exprdef,
                    CASE am.amname
                        WHEN 'prefix' THEN
                            CASE (option & 1)
                                WHEN 1 THEN 'DESC' ELSE 'ASC'
                            END
                    END as ordering,
                    c2.reloptions as attoptions
                FROM (
                    SELECT
                        row_number() OVER () as rnum, *,
                        unnest(i.indkey) as key, unnest(i.indoption) as option
                    FROM pg_index i
                ) idx
                LEFT JOIN pg_class c ON idx.indrelid = c.oid
                LEFT JOIN pg_class c2 ON idx.indexrelid = c2.oid
                LEFT JOIN pg_am am ON c2.relam = am.oid
                LEFT JOIN pg_attribute attr ON attr.attrelid = c.oid AND attr.attnum = idx.key
                WHERE c.relname = %s
            ) s2
            GROUP BY indexname, indisunique, indisprimary, amname, exprdef, attoptions;
        """, [table_name])
        for index, columns, unique, primary, orders, type_, definition, options in cursor.fetchall():
            if index not in constraints:
                constraints[index] = {
                    "columns": columns if columns != [None] else [],
                    "orders": orders if orders != [None] else [],
                    "primary_key": primary,
                    "unique": unique,
                    "foreign_key": None,
                    "check": False,
                    "index": True,
                    # indexes are named 'prefix' in cockroachdb (as opposed
                    # to 'btree' in PostgreSQL).
                    "type": Index.suffix if type_ == 'prefix' else type_,
                    "definition": definition,
                    "options": options,
                }
        return constraints
