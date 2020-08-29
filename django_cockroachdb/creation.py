import os
import subprocess
import sys
from unittest import expectedFailure, skip

from django.conf import settings
from django.db import connections
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
            'schema.tests.SchemaTests.test_char_field_with_db_index_to_fk',
            'schema.tests.SchemaTests.test_m2m_rename_field_in_target_model',
            'schema.tests.SchemaTests.test_rename',
            'schema.tests.SchemaTests.test_text_field_with_db_index_to_fk',
            # cockroachdb doesn't support dropping the primary key.
            'schema.tests.SchemaTests.test_alter_int_pk_to_int_unique',
            # cockroachdb doesn't support changing the primary key of table.
            'schema.tests.SchemaTests.test_alter_not_unique_field_to_primary_key',
            'schema.tests.SchemaTests.test_primary_key',
            # SmallAutoField doesn't work:
            # https://github.com/cockroachdb/cockroach-django/issues/84
            'many_to_one.tests.ManyToOneTests.test_fk_to_smallautofield',
            'migrations.test_operations.OperationTests.test_smallfield_autofield_foreignfield_growth',
            'migrations.test_operations.OperationTests.test_smallfield_bigautofield_foreignfield_growth',
            # This backend raises "ValueError: CockroachDB's EXPLAIN doesn't
            # support any formats." instead of an "unknown format" error.
            'queries.test_explain.ExplainTests.test_unknown_format',
        )
        if self.connection.features.is_cockroachdb_20_1:
            expected_failures += (
                # timezones after 2038 use incorrect DST settings:
                # https://github.com/cockroachdb/django-cockroachdb/issues/124
                'expressions.tests.FTimeDeltaTests.test_datetime_subtraction_microseconds',
            )
        if not self.connection.features.is_cockroachdb_20_1:
            expected_failures += (
                # CAST timestamptz to time doesn't respect active time zone:
                # https://github.com/cockroachdb/django-cockroachdb/issues/37
                'db_functions.comparison.test_cast.CastTests.test_cast_from_db_datetime_to_time',
                # DATE_TRUNC result is incorrectly localized when a timezone is set:
                # https://github.com/cockroachdb/django-cockroachdb/issues/32
                'admin_views.test_templatetags.DateHierarchyTests.test_choice_links',
                'admin_views.tests.DateHierarchyTests.test_multiple_years',
                'admin_views.tests.DateHierarchyTests.test_related_field',
                'admin_views.tests.DateHierarchyTests.test_single',
                'admin_views.tests.DateHierarchyTests.test_within_month',
                'admin_views.tests.DateHierarchyTests.test_within_year',
                'admin_views.tests.AdminViewBasicTest.test_date_hierarchy_timezone_dst',
                'aggregation.tests.AggregateTestCase.test_dates_with_aggregation',
                'aggregation_regress.tests.AggregationTests.test_more_more_more',
                'backends.tests.DateQuotingTest.test_django_date_trunc',
                'dates.tests.DatesTests.test_dates_trunc_datetime_fields',
                'dates.tests.DatesTests.test_related_model_traverse',
                'datetimes.tests.DateTimesTests.test_21432',
                'datetimes.tests.DateTimesTests.test_datetimes_has_lazy_iterator',
                'datetimes.tests.DateTimesTests.test_datetimes_returns_available_dates_for_given_scope_and_given_field',  # noqa
                'datetimes.tests.DateTimesTests.test_related_model_traverse',
                'db_functions.datetime.test_extract_trunc.DateFunctionTests.test_trunc_day_func',
                'db_functions.datetime.test_extract_trunc.DateFunctionTests.test_trunc_func',
                'db_functions.datetime.test_extract_trunc.DateFunctionTests.test_trunc_subquery_with_parameters',
                'db_functions.datetime.test_extract_trunc.DateFunctionTests.test_trunc_month_func',
                'db_functions.datetime.test_extract_trunc.DateFunctionTests.test_trunc_quarter_func',
                'db_functions.datetime.test_extract_trunc.DateFunctionTests.test_trunc_time_func',
                'db_functions.datetime.test_extract_trunc.DateFunctionTests.test_trunc_week_func',
                'db_functions.datetime.test_extract_trunc.DateFunctionTests.test_trunc_year_func',
                'generic_views.test_dates.MonthArchiveViewTests.test_month_view',
                'generic_views.test_dates.MonthArchiveViewTests.test_month_view_allow_future',
                'generic_views.test_dates.MonthArchiveViewTests.test_month_view_get_month_from_request',
                'generic_views.test_dates.YearArchiveViewTests.test_year_view',
                'generic_views.test_dates.YearArchiveViewTests.test_year_view_allow_future',
                'generic_views.test_dates.YearArchiveViewTests.test_year_view_custom_sort_order',
                'generic_views.test_dates.YearArchiveViewTests.test_year_view_make_object_list',
                'generic_views.test_dates.YearArchiveViewTests.test_year_view_two_custom_sort_orders',
                # Because DateFunctionWithTimeZoneTests inherits DateFunctionTests,
                # these tests give "unexpected successes when they pass in the
                # superclass.
                'db_functions.datetime.test_extract_trunc.DateFunctionWithTimeZoneTests.test_trunc_func',
                'db_functions.datetime.test_extract_trunc.DateFunctionWithTimeZoneTests.test_trunc_func_with_timezone',
                'db_functions.datetime.test_extract_trunc.DateFunctionWithTimeZoneTests.test_trunc_week_func',
                'db_functions.datetime.test_extract_trunc.DateFunctionWithTimeZoneTests.test_trunc_hour_func',
                'db_functions.datetime.test_extract_trunc.DateFunctionWithTimeZoneTests.test_trunc_minute_func',
                'db_functions.datetime.test_extract_trunc.DateFunctionWithTimeZoneTests.test_trunc_second_func',
                'db_functions.datetime.test_extract_trunc.DateFunctionWithTimeZoneTests.test_trunc_timezone_applied_before_truncation',  # noqa
                'db_functions.datetime.test_extract_trunc.DateFunctionWithTimeZoneTests.test_trunc_ambiguous_and_invalid_times',  # noqa
                'extra_regress.tests.ExtraRegressTests.test_dates_query',
                'many_to_one.tests.ManyToOneTests.test_select_related',
                'model_inheritance_regress.tests.ModelInheritanceTest.test_issue_7105',
                'model_regress.tests.ModelTests.test_date_filter_null',
                'multiple_database.tests.QueryTestCase.test_basic_queries',
                'queries.tests.Queries1Tests.test_ticket7155',
                'queries.tests.Queries1Tests.test_tickets_6180_6203',
                'queries.tests.Queries1Tests.test_tickets_7087_12242',
                'reserved_names.tests.ReservedNameTests.test_dates',
                'timezones.tests.LegacyDatabaseTests.test_query_datetime_lookups',
                'timezones.tests.LegacyDatabaseTests.test_query_datetimes',
                'timezones.tests.NewDatabaseTests.test_query_datetimes',
                'timezones.tests.NewDatabaseTests.test_query_datetimes_in_other_timezone',
                # Unsupported query: unknown signature: extract(string, interval)
                # https://github.com/cockroachdb/django-cockroachdb/issues/29
                'db_functions.datetime.test_extract_trunc.DateFunctionTests.test_extract_duration',
                'db_functions.datetime.test_extract_trunc.DateFunctionWithTimeZoneTests.test_extract_duration',
                # timezone() doesn't support UTC offsets:
                # https://github.com/cockroachdb/django-cockroachdb/issues/97
                'db_functions.datetime.test_extract_trunc.DateFunctionWithTimeZoneTests.test_extract_func_with_timezone',  # noqa
                # extract() doesn't respect active time zone:
                # https://github.com/cockroachdb/django-cockroachdb/issues/47
                'db_functions.datetime.test_extract_trunc.DateFunctionTests.test_extract_func',
                'db_functions.datetime.test_extract_trunc.DateFunctionTests.test_extract_hour_func',
                # log(b, x) not supported: https://github.com/cockroachdb/django-cockroachdb/issues/50
                'db_functions.math.test_log.LogTests.test_decimal',
                'db_functions.math.test_log.LogTests.test_float',
                'db_functions.math.test_log.LogTests.test_integer',
                'db_functions.math.test_log.LogTests.test_null',
                # Incorrect interval math on date columns when a time zone is set:
                # https://github.com/cockroachdb/django-cockroachdb/issues/53
                'expressions.tests.FTimeDeltaTests.test_date_comparison',
                # Interval math across dst works differently from other databases.
                # https://github.com/cockroachdb/django-cockroachdb/issues/54
                'expressions.tests.FTimeDeltaTests.test_delta_update',
                'expressions.tests.FTimeDeltaTests.test_duration_with_datetime_microseconds',
                # Tests that require savepoints:
                'admin_inlines.tests.TestReadOnlyChangeViewInlinePermissions.test_add_url_not_allowed',
                'admin_views.tests.AdminViewBasicTest.test_disallowed_to_field',
                'admin_views.tests.AdminViewPermissionsTest.test_add_view',
                'admin_views.tests.AdminViewPermissionsTest.test_change_view',
                'admin_views.tests.AdminViewPermissionsTest.test_change_view_save_as_new',
                'admin_views.tests.AdminViewPermissionsTest.test_delete_view',
                'admin_views.tests.GroupAdminTest.test_group_permission_performance',
                'admin_views.tests.UserAdminTest.test_user_permission_performance',
                'auth_tests.test_views.ChangelistTests.test_view_user_password_is_readonly',
                'fixtures.tests.FixtureLoadingTests.test_loaddata_app_option',
                'fixtures.tests.FixtureLoadingTests.test_unmatched_identifier_loading',
                'fixtures_model_package.tests.FixtureTestCase.test_loaddata',
                'force_insert_update.tests.ForceTests.test_force_update',
                'get_or_create.tests.GetOrCreateTests.test_get_or_create_invalid_params',
                'get_or_create.tests.GetOrCreateTestsWithManualPKs.test_create_with_duplicate_primary_key',
                'get_or_create.tests.GetOrCreateTestsWithManualPKs.test_get_or_create_raises_IntegrityError_plus_traceback', # noqa
                'get_or_create.tests.GetOrCreateTestsWithManualPKs.test_savepoint_rollback',
                'get_or_create.tests.GetOrCreateThroughManyToMany.test_something',
                'get_or_create.tests.UpdateOrCreateTests.test_integrity',
                'get_or_create.tests.UpdateOrCreateTests.test_manual_primary_key_test',
                'get_or_create.tests.UpdateOrCreateTestsWithManualPKs.test_create_with_duplicate_primary_key',
                'many_to_one.tests.ManyToOneTests.test_fk_assignment_and_related_object_cache',
                'many_to_many.tests.ManyToManyTests.test_add',
                'model_fields.test_booleanfield.BooleanFieldTests.test_null_default',
                'model_fields.test_floatfield.TestFloatField.test_float_validates_object',
                'multiple_database.tests.QueryTestCase.test_generic_key_cross_database_protection',
                'multiple_database.tests.QueryTestCase.test_m2m_cross_database_protection',
                'transaction_hooks.tests.TestConnectionOnCommit.test_discards_hooks_from_rolled_back_savepoint',
                'transaction_hooks.tests.TestConnectionOnCommit.test_inner_savepoint_rolled_back_with_outer',
                'transaction_hooks.tests.TestConnectionOnCommit.test_inner_savepoint_does_not_affect_outer',
                # CharField max_length is ignored on cockroachdb. CharField is
                # introspected as TextField.
                'introspection.tests.IntrospectionTests.test_get_table_description_col_lengths',
            )
        if not self.connection.features.is_cockroachdb_20_2:
            expected_failures += (
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
        if not self.connection.features.is_cockroachdb_20_1:
            skip_classes += (
                # Requires savepoints:
                'test_utils.tests.TestBadSetUpTestData',
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
            # The cockroach tests are run with a fork of Django that fixes
            # a bug where TestCase doesn't work without savepoints
            # (https://code.djangoproject.com/ticket/28263).
            for alias in connections:
                connections[alias].features._supports_transactions = True
            self.mark_expected_failures()
        super().create_test_db(*args, **kwargs)

    def _clone_test_db(self, suffix, verbosity, keepdb=False):
        source_database_name = self.connection.settings_dict['NAME']
        target_database_name = self.get_test_db_clone_settings(suffix)['NAME']
        test_db_params = {
            'dbname': self.connection.ops.quote_name(target_database_name),
            'suffix': self.sql_table_creation_suffix(),
        }
        with self._nodb_connection.cursor() as cursor:
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
        # Chop off ['cockroach', 'sql', '--database=test_djangotests', ...]
        connect_args = DatabaseClient.settings_to_cmd_args(self.connection.settings_dict)[3:]
        dump_cmd = ['cockroach', 'dump', source_database_name] + connect_args
        load_cmd = ['cockroach', 'sql', '-d', target_database_name] + connect_args
        with subprocess.Popen(dump_cmd, stdout=subprocess.PIPE) as dump_proc:
            with subprocess.Popen(load_cmd, stdin=dump_proc.stdout, stdout=subprocess.DEVNULL):
                # Allow dump_proc to receive a SIGPIPE if the load process exits.
                dump_proc.stdout.close()
