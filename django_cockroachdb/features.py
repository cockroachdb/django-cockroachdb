import operator

from django.db.backends.postgresql.features import (
    DatabaseFeatures as PostgresDatabaseFeatures,
)
from django.utils.functional import cached_property


class DatabaseFeatures(PostgresDatabaseFeatures):
    # Cloning databases doesn't speed up tests.
    # https://github.com/cockroachdb/django-cockroachdb/issues/206
    can_clone_databases = False

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

    @cached_property
    def django_test_expected_failures(self):
        expected_failures = {
            # sum(): unsupported binary operator: <float> + <int>:
            # https://github.com/cockroachdb/django-cockroachdb/issues/73
            'aggregation.tests.AggregateTestCase.test_add_implementation',
            'aggregation.tests.AggregateTestCase.test_combine_different_types',
            # greatest(): expected avg(price) to be of type float, found type
            # decimal: https://github.com/cockroachdb/django-cockroachdb/issues/74
            'aggregation.tests.AggregateTestCase.test_expression_on_aggregation',
            # POWER() doesn't support negative exponents:
            # https://github.com/cockroachdb/django-cockroachdb/issues/22
            'db_functions.math.test_power.PowerTests.test_integer',
            # Tests that assume a serial pk: https://github.com/cockroachdb/django-cockroachdb/issues/18
            'admin_views.tests.AdminViewPermissionsTest.test_history_view',
            'aggregation_regress.tests.AggregationTests.test_more_more',
            'aggregation_regress.tests.AggregationTests.test_more_more_more',
            'aggregation_regress.tests.AggregationTests.test_ticket_11293',
            'defer_regress.tests.DeferRegressionTest.test_ticket_23270',
            'distinct_on_fields.tests.DistinctOnTests.test_basic_distinct_on',
            'generic_relations_regress.tests.GenericRelationTests.test_annotate',
            'migrations.test_operations.OperationTests.test_alter_order_with_respect_to',
            'model_formsets_regress.tests.FormfieldShouldDeleteFormTests.test_custom_delete',
            'multiple_database.tests.RouterTestCase.test_generic_key_cross_database_protection',
            'ordering.tests.OrderingTests.test_order_by_fk_attname',
            'ordering.tests.OrderingTests.test_order_by_pk',
            'queries.test_bulk_update.BulkUpdateNoteTests.test_multiple_fields',
            'queries.test_bulk_update.BulkUpdateTests.test_inherited_fields',
            'queries.tests.Queries1Tests.test_ticket9411',
            'queries.tests.RelatedLookupTypeTests.test_values_queryset_lookup',
            'syndication_tests.tests.SyndicationFeedTest.test_rss2_feed',
            'syndication_tests.tests.SyndicationFeedTest.test_latest_post_date',
            'syndication_tests.tests.SyndicationFeedTest.test_rss091_feed',
            'syndication_tests.tests.SyndicationFeedTest.test_template_feed',
            # unknown function: sha224() and sha384():
            # https://github.com/cockroachdb/django-cockroachdb/issues/81
            'db_functions.text.test_sha224.SHA224Tests.test_basic',
            'db_functions.text.test_sha224.SHA224Tests.test_transform',
            'db_functions.text.test_sha384.SHA384Tests.test_basic',
            'db_functions.text.test_sha384.SHA384Tests.test_transform',
            # Unsupported query: mixed type addition in SELECT:
            # https://github.com/cockroachdb/django-cockroachdb/issues/19
            'annotations.tests.NonAggregateAnnotationTestCase.test_mixed_type_annotation_numbers',
            # Forward references in fixtures won't work until CockroachDB can
            # disable constraints: https://github.com/cockroachdb/cockroach/issues/19444
            'backends.base.test_creation.TestDeserializeDbFromString.test_circular_reference',
            'backends.base.test_creation.TestDeserializeDbFromString.test_circular_reference_with_natural_key',
            'backends.base.test_creation.TestDeserializeDbFromString.test_self_reference',
            'fixtures.tests.CircularReferenceTests.test_circular_reference',
            'fixtures.tests.ForwardReferenceTests.test_forward_reference_fk',
            'fixtures.tests.ForwardReferenceTests.test_forward_reference_m2m',
            'serializers.test_data.SerializerDataTests.test_json_serializer',
            'serializers.test_data.SerializerDataTests.test_python_serializer',
            'serializers.test_data.SerializerDataTests.test_xml_serializer',
            'serializers.test_data.SerializerDataTests.test_yaml_serializer',
            # No sequence for AutoField in CockroachDB.
            'introspection.tests.IntrospectionTests.test_sequence_list',
            # Unsupported query: unsupported binary operator: <int> / <int>:
            # https://github.com/cockroachdb/django-cockroachdb/issues/21
            'expressions.tests.ExpressionOperatorTests.test_lefthand_division',
            'expressions.tests.ExpressionOperatorTests.test_right_hand_division',
            # CockroachDB doesn't support disabling constraints:
            # https://github.com/cockroachdb/cockroach/issues/19444
            'auth_tests.test_views.UUIDUserTests.test_admin_password_change',
            'backends.tests.FkConstraintsTests.test_check_constraints',
            'backends.tests.FkConstraintsTests.test_disable_constraint_checks_context_manager',
            'backends.tests.FkConstraintsTests.test_disable_constraint_checks_manually',
            # Passing a naive datetime to cursor.execute() probably can't work
            # on CockroachDB. The value needs a timezone so psycopg2 will cast
            # it to timestamptz rather than timestamp to avoid "value type
            # timestamp doesn't match type timestamptz of column "dt"" but
            # there aren't any hooks to do that.
            'timezones.tests.LegacyDatabaseTests.test_cursor_execute_accepts_naive_datetime',
            # SchemaEditor._model_indexes_sql() doesn't output some expected
            # tablespace SQL because CockroachDB automatically indexes foreign
            # keys.
            'model_options.test_tablespaces.TablespacesTests.test_tablespace_for_many_to_many_field',
            # Unsupported type conversion: https://github.com/cockroachdb/cockroach/issues/9851
            'migrations.test_executor.ExecutorTests.test_alter_id_type_with_fk',
            'migrations.test_operations.OperationTests.test_alter_field_pk_fk',
            'migrations.test_operations.OperationTests.test_alter_field_reloads_state_on_fk_target_changes',
            'migrations.test_operations.OperationTests.test_alter_field_reloads_state_on_fk_with_to_field_related_name_target_type_change',  # noqa
            'migrations.test_operations.OperationTests.test_alter_field_reloads_state_on_fk_with_to_field_target_changes',  # noqa
            'migrations.test_operations.OperationTests.test_alter_field_reloads_state_on_fk_with_to_field_target_type_change',  # noqa
            'migrations.test_operations.OperationTests.test_alter_fk_non_fk',
            'migrations.test_operations.OperationTests.test_rename_field_reloads_state_on_fk_target_changes',
            'schema.tests.SchemaTests.test_alter_auto_field_to_char_field',
            'schema.tests.SchemaTests.test_alter_autofield_pk_to_smallautofield_pk_sequence_owner',
            'schema.tests.SchemaTests.test_alter_text_field_to_date_field',
            'schema.tests.SchemaTests.test_alter_text_field_to_datetime_field',
            'schema.tests.SchemaTests.test_alter_text_field_to_time_field',
            'schema.tests.SchemaTests.test_alter_textual_field_keep_null_status',
            'schema.tests.SchemaTests.test_char_field_pk_to_auto_field',
            'schema.tests.SchemaTests.test_char_field_with_db_index_to_fk',
            'schema.tests.SchemaTests.test_m2m_rename_field_in_target_model',
            'schema.tests.SchemaTests.test_rename',
            'schema.tests.SchemaTests.test_text_field_with_db_index_to_fk',
            # CockroachDB doesn't support dropping the primary key.
            'schema.tests.SchemaTests.test_alter_int_pk_to_int_unique',
            # CockroachDB doesn't support changing the primary key of table.
            'schema.tests.SchemaTests.test_alter_not_unique_field_to_primary_key',
            'schema.tests.SchemaTests.test_primary_key',
            # SmallAutoField doesn't work:
            # https://github.com/cockroachdb/cockroach-django/issues/84
            'bulk_create.tests.BulkCreateTests.test_bulk_insert_nullable_fields',
            'many_to_one.tests.ManyToOneTests.test_fk_to_smallautofield',
            'migrations.test_operations.OperationTests.test_smallfield_autofield_foreignfield_growth',
            'migrations.test_operations.OperationTests.test_smallfield_bigautofield_foreignfield_growth',
            # This backend raises "ValueError: CockroachDB's EXPLAIN doesn't
            # support any formats." instead of an "unknown format" error.
            'queries.test_explain.ExplainTests.test_unknown_format',
            # timezones after 2038 use incorrect DST settings:
            # https://github.com/cockroachdb/django-cockroachdb/issues/124
            'expressions.tests.FTimeDeltaTests.test_datetime_subtraction_microseconds',
            # unsupported comparison operator: <jsonb> > <string>:
            # https://github.com/cockroachdb/cockroach/issues/49144
            'model_fields.test_jsonfield.TestQuerying.test_deep_lookup_transform',
            # ordering by JSON isn't supported:
            # https://github.com/cockroachdb/cockroach/issues/35706
            'model_fields.test_jsonfield.TestQuerying.test_deep_distinct',
            'model_fields.test_jsonfield.TestQuerying.test_order_grouping_custom_decoder',
            'model_fields.test_jsonfield.TestQuerying.test_ordering_by_transform',
            'model_fields.test_jsonfield.TestQuerying.test_ordering_grouping_by_key_transform',
        }
        if not self.connection.features.is_cockroachdb_20_2:
            expected_failures.update({
                # stddev/variance functions not supported:
                # https://github.com/cockroachdb/django-cockroachdb/issues/25
                'aggregation.test_filter_argument.FilteredAggregateTests.test_filtered_numerical_aggregates',
                'aggregation_regress.tests.AggregationTests.test_stddev',
                # Nondeterministic query: https://github.com/cockroachdb/django-cockroachdb/issues/48
                'queries.tests.SubqueryTests.test_slice_subquery_and_query',
                # `SHOW TABLES` doesn't distinguish between tables and views.
                # Both are included regardless of whether inspectdb's
                # --include-views option is set.
                'inspectdb.tests.InspectDBTransactionalTests.test_include_views',
                'introspection.tests.IntrospectionTests.test_table_names_with_views',
                # excluding null json keys incorrectly returns values where the
                # key doesn't exist: https://github.com/cockroachdb/cockroach/issues/49143
                'model_fields.test_jsonfield.TestQuerying.test_none_key_exclude',
            })
        return expected_failures

    django_test_skips = {
        # https://github.com/cockroachdb/django-cockroachdb/issues/20
        'Unsupported query: UPDATE float column with integer column.': {
            'expressions.tests.ExpressionsNumericTests',
        },
        # https://github.com/cockroachdb/django-cockroachdb/issues/153#issuecomment-664697963
        'CockroachDB has more restrictive blocking than other databases.': {
            'select_for_update.tests.SelectForUpdateTests.test_block',
        },
        # https://www.cockroachlabs.com/docs/stable/transaction-retry-error-reference.html#retry_write_too_old
        'Fails with TransactionRetryWithProtoRefreshError: ... RETRY_WRITE_TOO_OLD ...': {
            'delete_regress.tests.DeleteLockingTest.test_concurrent_delete',
        },
        'Skip to prevents some error output in the logs.': {
            # Since QuerySet.select_for_update() was enabled, this test is
            # already skipped by the 'Database took too long to lock the row'
            # logic in the test. Skipping it entirely prevents some error
            # output in the logs:
            # Exception in thread Thread-1:
            # ...
            # psycopg2.errors.SerializationFailure: restart transaction:
            # TransactionRetryWithProtoRefreshError: WriteTooOldError: write
            # at timestamp 1598314405.858850941,0 too old; wrote at
            # 1598314405.883337663,1
            'get_or_create.tests.UpdateOrCreateTransactionTests.test_creation_in_transaction',
            # Sometimes fails as above or with
            # AssertionError: datetime.timedelta(microseconds=28529) not
            # greater than datetime.timedelta(microseconds=500000)
            'get_or_create.tests.UpdateOrCreateTransactionTests.test_updates_in_transaction',
        },
    }
