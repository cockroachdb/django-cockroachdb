import os
import subprocess
import sys
from unittest import expectedFailure, skip

from django.conf import settings
from django.db.backends.postgresql.creation import (
    DatabaseCreation as PostgresDatabaseCreation,
)
from django.utils.module_loading import import_string

from .client import DatabaseClient


class DatabaseCreation(PostgresDatabaseCreation):

    def mark_expected_failures(self):
        """Mark tests that don't work on cockroachdb as expected failures."""
        expected_failures = (
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
            # Transaction issues: https://github.com/cockroachdb/django-cockroachdb/issues/14
            'delete_regress.tests.DeleteLockingTest.test_concurrent_delete',
            # unknown function: sha224() and sha384():
            # https://github.com/cockroachdb/django-cockroachdb/issues/81
            'db_functions.text.test_sha224.SHA224Tests.test_basic',
            'db_functions.text.test_sha224.SHA224Tests.test_transform',
            'db_functions.text.test_sha384.SHA384Tests.test_basic',
            'db_functions.text.test_sha384.SHA384Tests.test_transform',
            # Unsupported query: mixed type addition in SELECT:
            # https://github.com/cockroachdb/django-cockroachdb/issues/19
            'annotations.tests.NonAggregateAnnotationTestCase.test_mixed_type_annotation_numbers',
            # Forward references in fixtures won't work until cockroachdb can
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
            # No sequence for AutoField in cockroachdb.
            'introspection.tests.IntrospectionTests.test_sequence_list',
            # Unsupported query: unsupported binary operator: <int> / <int>:
            # https://github.com/cockroachdb/django-cockroachdb/issues/21
            'expressions.tests.ExpressionOperatorTests.test_lefthand_division',
            'expressions.tests.ExpressionOperatorTests.test_right_hand_division',
            # cockroachdb doesn't support disabling constraints:
            # https://github.com/cockroachdb/cockroach/issues/19444
            'auth_tests.test_views.UUIDUserTests.test_admin_password_change',
            'backends.tests.FkConstraintsTests.test_check_constraints',
            'backends.tests.FkConstraintsTests.test_disable_constraint_checks_context_manager',
            'backends.tests.FkConstraintsTests.test_disable_constraint_checks_manually',
            # Passing a naive datetime to cursor.execute() probably can't work
            # on cockroachdb. The value needs a timezone so psycopg2 will cast
            # it to timestamptz rather than timestamp to avoid "value type
            # timestamp doesn't match type timestamptz of column "dt"" but
            # there aren't any hooks to do that.
            'timezones.tests.LegacyDatabaseTests.test_cursor_execute_accepts_naive_datetime',
            # SchemaEditor._model_indexes_sql() doesn't output some expected
            # tablespace SQL because cockroachdb automatically indexes foreign
            # keys.
            'model_options.test_tablespaces.TablespacesTests.test_tablespace_for_many_to_many_field',
            # ALTER COLUMN TYPE requiring rewrite of on-disk data is currently
            # not supported for columns that are part of an index.
            # https://go.crdb.dev/issue/47636
            'migrations.test_executor.ExecutorTests.test_alter_id_type_with_fk',
            'migrations.test_operations.OperationTests.test_alter_field_pk_fk',
            'migrations.test_operations.OperationTests.test_alter_field_reloads_state_on_fk_target_changes',
            'migrations.test_operations.OperationTests.test_alter_field_reloads_state_on_fk_with_to_field_related_name_target_type_change',  # noqa
            'migrations.test_operations.OperationTests.test_alter_field_reloads_state_on_fk_with_to_field_target_changes',  # noqa
            'migrations.test_operations.OperationTests.test_alter_field_reloads_state_on_fk_with_to_field_target_type_change',  # noqa
            'migrations.test_operations.OperationTests.test_rename_field_reloads_state_on_fk_target_changes',
            'schema.tests.SchemaTests.test_alter_auto_field_to_char_field',
            'schema.tests.SchemaTests.test_alter_autofield_pk_to_smallautofield_pk_sequence_owner',
            'schema.tests.SchemaTests.test_char_field_pk_to_auto_field',
            'schema.tests.SchemaTests.test_char_field_with_db_index_to_fk',
            'schema.tests.SchemaTests.test_text_field_with_db_index_to_fk',
            # cockroachdb doesn't support dropping the primary key.
            'schema.tests.SchemaTests.test_alter_int_pk_to_int_unique',
            # cockroachdb doesn't support changing the primary key of table.
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
            # excluding null json keys incorrectly returns values where the
            # key doesn't exist: https://github.com/cockroachdb/cockroach/issues/49143
            'model_fields.test_jsonfield.TestQuerying.test_none_key_exclude',
            # ordering by JSON isn't supported:
            # https://github.com/cockroachdb/cockroach/issues/35706
            'model_fields.test_jsonfield.TestQuerying.test_deep_distinct',
            'model_fields.test_jsonfield.TestQuerying.test_order_grouping_custom_decoder',
            'model_fields.test_jsonfield.TestQuerying.test_ordering_by_transform',
            'model_fields.test_jsonfield.TestQuerying.test_ordering_grouping_by_key_transform',
        )
        if not self.connection.features.is_cockroachdb_20_2:
            expected_failures += (
                # stddev/variance functions not supported:
                # https://github.com/cockroachdb/django-cockroachdb/issues/25
                'aggregation.test_filter_argument.FilteredAggregateTests.test_filtered_numerical_aggregates',
                'aggregation_regress.tests.AggregationTests.test_stddev',
                # Nondeterministic query: https://github.com/cockroachdb/django-cockroachdb/issues/48
                'queries.tests.SubqueryTests.test_slice_subquery_and_query',
                # Unsupported type conversion: https://github.com/cockroachdb/cockroach/issues/9851
                'migrations.test_operations.OperationTests.test_alter_fk_non_fk',
                'schema.tests.SchemaTests.test_alter_text_field_to_date_field',
                'schema.tests.SchemaTests.test_alter_text_field_to_datetime_field',
                'schema.tests.SchemaTests.test_alter_text_field_to_time_field',
                'schema.tests.SchemaTests.test_alter_textual_field_keep_null_status',
                'schema.tests.SchemaTests.test_m2m_rename_field_in_target_model',
                'schema.tests.SchemaTests.test_rename',
                # `SHOW TABLES` doesn't distinguish between tables and views.
                # Both are included regardless of whether inspectdb's
                # --include-views option is set.
                'inspectdb.tests.InspectDBTransactionalTests.test_include_views',
                'introspection.tests.IntrospectionTests.test_table_names_with_views',
            )
        for test_name in expected_failures:
            test_case_name, _, method_name = test_name.rpartition('.')
            test_app = test_name.split('.')[0]
            # Importing a test app that isn't installed raises RuntimeError.
            if test_app in settings.INSTALLED_APPS:
                test_case = import_string(test_case_name)
                method = getattr(test_case, method_name)
                setattr(test_case, method_name, expectedFailure(method))

        skip_classes = (
            # Unsupported query: UPDATE float column with integer column:
            # Number.objects.update(float=F('integer')) in setUpTestData(c)
            # https://github.com/cockroachdb/django-cockroachdb/issues/20
            'expressions.tests.ExpressionsNumericTests',
        )
        for test_class in skip_classes:
            test_module_name, _, test_class_name = test_class.rpartition('.')
            test_app = test_module_name.split('.')[0]
            if test_app in settings.INSTALLED_APPS:
                test_module = import_string(test_module_name)
                klass = getattr(test_module, test_class_name)
                setattr(test_module, test_class_name, skip('unsupported by cockroachdb')(klass))

        skip_tests = (
            # CockroachDB has more restrictive blocking than other databases.
            # https://github.com/cockroachdb/django-cockroachdb/issues/153#issuecomment-664697963
            'select_for_update.tests.SelectForUpdateTests.test_block',
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
        )
        for test_name in skip_tests:
            test_case_name, _, method_name = test_name.rpartition('.')
            test_app = test_name.split('.')[0]
            # Importing a test app that isn't installed raises RuntimeError.
            if test_app in settings.INSTALLED_APPS:
                test_case = import_string(test_case_name)
                method = getattr(test_case, method_name)
                setattr(test_case, method_name, skip('unsupported by cockroachdb')(method))

    def create_test_db(self, *args, **kwargs):
        # This environment variable is set by teamcity-build/runtests.py or
        # by a developer running the tests locally.
        if os.environ.get('RUNNING_COCKROACH_BACKEND_TESTS'):
            self.mark_expected_failures()
        super().create_test_db(*args, **kwargs)

    def _clone_test_db(self, suffix, verbosity, keepdb=False):
        source_database_name = self.connection.settings_dict['NAME']
        target_database_name = self.get_test_db_clone_settings(suffix)['NAME']
        test_db_params = {
            'dbname': self.connection.ops.quote_name(target_database_name),
            'suffix': self.sql_table_creation_suffix(),
        }
        with self._nodb_cursor() as cursor:
            try:
                self._execute_create_test_db(cursor, test_db_params, keepdb)
            except Exception:
                if keepdb:
                    # If the database should be kept, skip everything else.
                    return
                try:
                    if verbosity >= 1:
                        self.log('Destroying old test database for alias %s...' % (
                            self._get_database_display_str(verbosity, target_database_name),
                        ))
                    cursor.execute('DROP DATABASE %(dbname)s' % test_db_params)
                    self._execute_create_test_db(cursor, test_db_params, keepdb)
                except Exception as e:
                    self.log('Got an error recreating the test database: %s' % e)
                    sys.exit(2)
        self._clone_db(source_database_name, target_database_name)

    def _clone_db(self, source_database_name, target_database_name):
        connect_args, env = DatabaseClient.settings_to_cmd_args_env(self.connection.settings_dict, [])
        # Chop off ['cockroach', 'sql', '--database=test_djangotests', ...]
        connect_args = connect_args[3:]
        dump_cmd = ['cockroach', 'dump', source_database_name] + connect_args
        load_cmd = ['cockroach', 'sql', '-d', target_database_name] + connect_args
        with subprocess.Popen(dump_cmd, stdout=subprocess.PIPE, env=env) as dump_proc:
            with subprocess.Popen(load_cmd, stdin=dump_proc.stdout, stdout=subprocess.DEVNULL, env=env):
                # Allow dump_proc to receive a SIGPIPE if the load process exits.
                dump_proc.stdout.close()
