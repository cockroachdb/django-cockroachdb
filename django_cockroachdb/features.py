import operator

from django.db.backends.postgresql.features import (
    DatabaseFeatures as PostgresDatabaseFeatures,
)
from django.utils.functional import cached_property


class DatabaseFeatures(PostgresDatabaseFeatures):
    # Not supported: https://github.com/cockroachdb/cockroach/issues/40476
    has_select_for_update_nowait = property(operator.attrgetter('is_cockroachdb_20_2'))
    has_select_for_update_skip_locked = False

    # Not supported: https://github.com/cockroachdb/cockroach/issues/31632
    can_defer_constraint_checks = False

    # Not supported: https://github.com/cockroachdb/cockroach/issues/48307
    supports_deferrable_unique_constraints = False

    # Not supported: https://github.com/cockroachdb/cockroach/issues/9683
    supports_partial_indexes = property(operator.attrgetter('is_cockroachdb_20_2'))

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
    introspected_small_auto_field_type = 'BigIntegerField'

    # adding a REFERENCES constraint while also adding a column via ALTER not
    # supported: https://github.com/cockroachdb/cockroach/issues/32917
    can_create_inline_fk = property(operator.attrgetter('is_cockroachdb_20_2'))

    # This can be removed when CockroachDB adds support for NULL FIRST/LAST:
    # https://github.com/cockroachdb/cockroach/issues/6224
    supports_order_by_nulls_modifier = False

    # CockroachDB stopped creating indexes on foreign keys in 20.2.
    indexes_foreign_keys = property(operator.attrgetter('is_not_cockroachdb_20_2'))

    @cached_property
    def is_cockroachdb_20_2(self):
        return self.connection.cockroachdb_version >= (20, 2)

    @cached_property
    def is_not_cockroachdb_20_2(self):
        return self.connection.cockroachdb_version < (20, 2)
