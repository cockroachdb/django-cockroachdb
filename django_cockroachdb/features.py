import operator

from django.db.backends.postgresql.features import (
    DatabaseFeatures as PostgresDatabaseFeatures,
)
from django.utils.functional import cached_property


class DatabaseFeatures(PostgresDatabaseFeatures):
    has_select_for_update = property(operator.attrgetter('is_cockroachdb_20_1'))
    has_select_for_update_of = property(operator.attrgetter('is_cockroachdb_20_1'))
    # Not supported: https://github.com/cockroachdb/cockroach/issues/40476
    has_select_for_update_nowait = property(operator.attrgetter('is_cockroachdb_20_2'))
    has_select_for_update_skip_locked = False

    # Not supported: https://github.com/cockroachdb/cockroach/issues/31632
    can_defer_constraint_checks = False

    # Not supported: https://github.com/cockroachdb/cockroach/issues/9683
    supports_partial_indexes = property(operator.attrgetter('is_cockroachdb_20_2'))

    uses_savepoints = property(operator.attrgetter('is_cockroachdb_20_1'))
    can_release_savepoints = property(operator.attrgetter('is_cockroachdb_20_1'))

    # Used by DatabaseCreation.create_test_db() to enable transactions when
    # running the Django test suite since properties can't be set directly.
    _supports_transactions = None

    @property
    def supports_transactions(self):
        # cockroachdb does support transactions, however, a bug in Django
        # (https://code.djangoproject.com/ticket/28263) breaks TestCase if
        # transactions are enabled but not savepoints. Disabling this only
        # affects tests: transactions won't be used to speed them up.
        return self._supports_transactions or self.is_cockroachdb_20_1

    # There are limitations on having DDL statements in a transaction:
    # https://www.cockroachlabs.com/docs/stable/known-limitations.html#schema-changes-within-transactions
    can_rollback_ddl = False

    # Not supported: https://github.com/cockroachdb/cockroach/issues/17511
    create_test_procedure_without_params_sql = None
    create_test_procedure_with_int_param_sql = None

    # Not supported: https://github.com/cockroachdb/cockroach/issues/20956
    supports_sequence_reset = False

    # Forward references in fixtures won't work until cockroachdb can
    # disable constraints: https://github.com/cockroachdb/cockroach/issues/19444
    supports_forward_references = False

    # Unlike PostgreSQL, cockroachdb doesn't support any EXPLAIN formats
    # ('JSON', 'TEXT', 'XML', and 'YAML').
    supported_explain_formats = set()

    # Not supported: https://github.com/cockroachdb/cockroach/issues/41645
    supports_regex_backreferencing = False

    # CockroachDB sorts NULL values first with ASC and last with DESC.
    # PostgreSQL behaves the opposite.
    nulls_order_largest = False

    # Introspection may work but 'CREATE MATERIALIZED VIEW' (required for the
    # test) isn't implemented: https://github.com/cockroachdb/cockroach/issues/41649
    can_introspect_materialized_views = property(operator.attrgetter('is_cockroachdb_20_2'))

    introspected_big_auto_field_type = 'BigIntegerField'

    # Column ordering is supported but older versions of CockroachDB don't
    # report column ordering: https://github.com/cockroachdb/cockroach/issues/42175
    supports_index_column_ordering = property(operator.attrgetter('is_cockroachdb_20_1'))

    # CockroachDB stopped creating indexes on foreign keys in 20.2.
    indexes_foreign_keys = property(operator.attrgetter('is_not_cockroachdb_20_2'))

    @cached_property
    def is_cockroachdb_20_1(self):
        return self.connection.cockroachdb_version >= (20, 1)

    @cached_property
    def is_cockroachdb_20_2(self):
        return self.connection.cockroachdb_version >= (20, 2)

    @cached_property
    def is_not_cockroachdb_20_2(self):
        return self.connection.cockroachdb_version < (20, 2)
