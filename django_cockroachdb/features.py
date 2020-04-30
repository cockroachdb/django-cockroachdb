import operator

from django.db.backends.postgresql.features import (
    DatabaseFeatures as PostgresDatabaseFeatures,
)
from django.utils.functional import cached_property


class DatabaseFeatures(PostgresDatabaseFeatures):
    # Not supported: https://github.com/cockroachdb/cockroach/issues/6583
    has_select_for_update = False
    has_select_for_update_nowait = False
    has_select_for_update_of = False
    has_select_for_update_skip_locked = False

    # Not supported: https://github.com/cockroachdb/cockroach/issues/31632
    can_defer_constraint_checks = False

    # Not supported: https://github.com/cockroachdb/cockroach/issues/9683
    supports_partial_indexes = False

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
    supports_callproc_kwargs = False
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

    # Column ordering is supported but older versions of CockroachDB don't
    # report column ordering: https://github.com/cockroachdb/cockroach/issues/42175
    supports_index_column_ordering = property(operator.attrgetter('is_cockroachdb_20_1'))

    # adding a REFERENCES constraint while also adding a column via ALTER not
    # supported: https://github.com/cockroachdb/cockroach/issues/32917
    can_create_inline_fk = False

    @cached_property
    def is_cockroachdb_20_1(self):
        return self.connection.cockroachdb_version >= (20, 1)
