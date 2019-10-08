from django.db.backends.postgresql.features import (
    DatabaseFeatures as PostgresDatabaseFeatures,
)


class DatabaseFeatures(PostgresDatabaseFeatures):
    """
    Not currently supported: https://github.com/cockroachdb/cockroach/issues/18656
    """
    has_select_for_update = False
    has_select_for_update_nowait = False
    has_select_for_update_of = False
    has_select_for_update_skip_locked = False

    """
    Not currently supported: https://github.com/cockroachdb/cockroach/issues/31632
    """
    can_defer_constraint_checks = False

    """
    Not currently supported: https://github.com/cockroachdb/cockroach/issues/9683
    """
    supports_partial_indexes = False

    """
    Not currently supported: https://github.com/cockroachdb/cockroach/issues/10735
    """
    uses_savepoints = False
    can_release_savepoints = False

    """
    There are some known limitations on having DDL statements in a transaction:
        https://www.cockroachlabs.com/docs/stable/known-limitations.html#schema-changes-within-transactions
    """
    can_rollback_ddl = False

    """
    Currently not supported: https://github.com/cockroachdb/cockroach/issues/17511
    """
    supports_callproc_kwargs = False
    create_test_procedure_without_params_sql = None
    create_test_procedure_with_int_param_sql = None

    """
    Currently not supported: https://github.com/cockroachdb/cockroach/issues/10735
    """
    atomic_transactions = False

    """
    Currently today in order to say we support transactions we have to be able
    to support nested transaction with savepoints:
        https://github.com/cockroachdb/cockroach/issues/10735
    """
    supports_transactions = False

    # Not implemented by cockroachdb: https://github.com/cockroachdb/cockroach/issues/20956
    supports_sequence_reset = False
