from django.db.backends.postgresql.features import (
    DatabaseFeatures as PostgresDatabaseFeatures,
)


class DatabaseFeatures(PostgresDatabaseFeatures):
    # Not supported: https://github.com/cockroachdb/cockroach/issues/40476
    has_select_for_update_nowait = False
    has_select_for_update_skip_locked = False

    # Not supported: https://github.com/cockroachdb/cockroach/issues/31632
    can_defer_constraint_checks = False

    # Not supported: https://github.com/cockroachdb/cockroach/issues/48307
    supports_deferrable_unique_constraints = False

    # Not supported: https://github.com/cockroachdb/cockroach/issues/9683
    supports_partial_indexes = False

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

    # Introspection may work but 'CREATE MATERIALIZED VIEW' (required for the
    # test) isn't implemented: https://github.com/cockroachdb/cockroach/issues/41649
    can_introspect_materialized_views = False

    introspected_big_auto_field_type = 'BigIntegerField'
    introspected_small_auto_field_type = 'BigIntegerField'

    # adding a REFERENCES constraint while also adding a column via ALTER not
    # supported: https://github.com/cockroachdb/cockroach/issues/32917
    can_create_inline_fk = False

    # This can be removed when CockroachDB adds support for NULL FIRST/LAST:
    # https://github.com/cockroachdb/cockroach/issues/6224
    supports_order_by_nulls_modifier = False
