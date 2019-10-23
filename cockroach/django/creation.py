import os
import subprocess
import sys
from unittest import expectedFailure

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
            # column must appear in the GROUP BY clause or be used in an aggregate function:
            # https://github.com/cockroachdb/cockroach-django/issues/13
            'annotations.tests.NonAggregateAnnotationTestCase.test_aggregate_over_annotation',
            'annotations.tests.NonAggregateAnnotationTestCase.test_annotate_with_aggregation',
            'annotations.tests.NonAggregateAnnotationTestCase.test_annotation_filter_with_subquery',
            'annotations.tests.NonAggregateAnnotationTestCase.test_filter_agg_with_double_f',
            'custom_managers.tests.CustomManagersRegressTestCase.test_refresh_from_db_when_default_manager_filters',
            'custom_managers.tests.CustomManagersRegressTestCase.test_save_clears_annotations_from_base_manager',
            'db_functions.comparison.test_cast.CastTests.test_cast_from_db_datetime_to_date_group_by',
            'defer_regress.tests.DeferAnnotateSelectRelatedTest.test_defer_annotate_select_related',
            'defer_regress.tests.DeferRegressionTest.test_basic',
            'defer_regress.tests.DeferRegressionTest.test_ticket_16409',
            'distinct_on_fields.tests.DistinctOnTests.test_distinct_not_implemented_checks',
            'lookup.test_decimalfield.DecimalFieldLookupTests.test_gt',
            'lookup.test_decimalfield.DecimalFieldLookupTests.test_gte',
            'lookup.test_decimalfield.DecimalFieldLookupTests.test_lt',
            'lookup.test_decimalfield.DecimalFieldLookupTests.test_lte',
            'queries.tests.Queries1Tests.test_ticket_20250',
            'queries.tests.ValuesQuerysetTests.test_named_values_list_with_fields',
            'queries.tests.ValuesQuerysetTests.test_named_values_list_without_fields',
            'queries.test_explain.ExplainTests.test_basic',
            'queryset_pickle.tests.PickleabilityTestCase.test_annotation_with_callable_default',
            # CAST timestamptz to time doesn't respect active time zone:
            # https://github.com/cockroachdb/cockroach-django/issues/37
            'db_functions.comparison.test_cast.CastTests.test_cast_from_db_datetime_to_time',
            # DATE_TRUNC result is incorrectly localized when a timezone is set:
            # https://github.com/cockroachdb/cockroach-django/issues/32
            'extra_regress.tests.ExtraRegressTests.test_dates_query',
            'many_to_one.tests.ManyToOneTests.test_select_related',
            'model_inheritance_regress.tests.ModelInheritanceTest.test_issue_7105',
            'model_regress.tests.ModelTests.test_date_filter_null',
            'multiple_database.tests.QueryTestCase.test_basic_queries',
            'queries.tests.Queries1Tests.test_ticket7155',
            'queries.tests.Queries1Tests.test_tickets_6180_6203',
            'queries.tests.Queries1Tests.test_tickets_7087_12242',
            'reserved_names.tests.ReservedNameTests.test_dates',
            # POWER() doesn't support negative exponents:
            # https://github.com/cockroachdb/cockroach-django/issues/22
            'db_functions.math.test_power.PowerTests.test_integer',
            # Tests that assume a serial pk: https://github.com/cockroachdb/cockroach-django/issues/18
            'defer_regress.tests.DeferRegressionTest.test_ticket_23270',
            'distinct_on_fields.tests.DistinctOnTests.test_basic_distinct_on',
            'generic_relations_regress.tests.GenericRelationTests.test_annotate',
            'm2m_through_regress.tests.ThroughLoadDataTestCase.test_sequence_creation',
            'model_formsets_regress.tests.FormfieldShouldDeleteFormTests.test_custom_delete',
            'ordering.tests.OrderingTests.test_order_by_fk_attname',
            'ordering.tests.OrderingTests.test_order_by_pk',
            'queries.test_bulk_update.BulkUpdateNoteTests.test_multiple_fields',
            'queries.test_bulk_update.BulkUpdateTests.test_inherited_fields',
            'queries.tests.Queries1Tests.test_ticket9411',
            'queries.tests.Ticket14056Tests.test_ticket_14056',
            'queries.tests.RelatedLookupTypeTests.test_values_queryset_lookup',
            # Transaction issues: https://github.com/cockroachdb/cockroach-django/issues/14
            'delete_regress.tests.DeleteLockingTest.test_concurrent_delete',
            # No support for NULLS FIRST/LAST: https://github.com/cockroachdb/cockroach-django/issues/17
            'admin_ordering.tests.TestAdminOrdering.test_specified_ordering_by_f_expression',
            'ordering.tests.OrderingTests.test_default_ordering_by_f_expression',
            'ordering.tests.OrderingTests.test_order_by_nulls_first',
            'ordering.tests.OrderingTests.test_order_by_nulls_last',
            'ordering.tests.OrderingTests.test_orders_nulls_first_on_filtered_subquery',
            # Tests that require savepoints:
            'force_insert_update.tests.ForceTests.test_force_update',
            'many_to_one.tests.ManyToOneTests.test_fk_assignment_and_related_object_cache',
            'many_to_many.tests.ManyToManyTests.test_add',
            'model_fields.test_booleanfield.BooleanFieldTests.test_null_default',
            'model_fields.test_floatfield.TestFloatField.test_float_validates_object',
            'transaction_hooks.tests.TestConnectionOnCommit.test_discards_hooks_from_rolled_back_savepoint',
            'transaction_hooks.tests.TestConnectionOnCommit.test_inner_savepoint_rolled_back_with_outer',
            'transaction_hooks.tests.TestConnectionOnCommit.test_inner_savepoint_does_not_affect_outer',
            # database connection isn't set to UTC (to be investigated)
            'admin_filters.tests.ListFiltersTests.test_datefieldlistfilter_with_time_zone_support',
            'model_fields.test_datetimefield.DateTimeFieldTests.test_lookup_date_with_use_tz',
            # unknown signature unnest(int2vector, int2vector):
            # https://github.com/cockroachdb/cockroach-django/issues/10
            'constraints.tests.CheckConstraintTests.test_name',
            'constraints.tests.UniqueConstraintTests.test_name',
            'proxy_models.tests.ProxyModelTests.test_proxy_load_from_fixture',
            # Unsupported query: mixed type addition in SELECT:
            # https://github.com/cockroachdb/cockroach-django/issues/19
            'annotations.tests.NonAggregateAnnotationTestCase.test_mixed_type_annotation_numbers',
            # Nondeterministic query: https://github.com/cockroachdb/cockroach-django/issues/48
            'queries.tests.SubqueryTests.test_slice_subquery_and_query',
            # log(b, x) not supported: https://github.com/cockroachdb/cockroach-django/issues/50
            'db_functions.math.test_log.LogTests.test_decimal',
            'db_functions.math.test_log.LogTests.test_float',
            'db_functions.math.test_log.LogTests.test_integer',
            'db_functions.math.test_log.LogTests.test_null',
            # Skipped for PostgreSQL but should be skipped for cockroachdb also:
            # https://github.com/cockroachdb/cockroach-django/issues/57
            'expressions_window.tests.WindowFunctionTests.test_range_n_preceding_and_following',
        )
        for test_name in expected_failures:
            test_case_name, _, method_name = test_name.rpartition('.')
            test_app = test_name.split('.')[0]
            # Importing a test app that isn't installed raises RuntimeError.
            if test_app in settings.INSTALLED_APPS:
                test_case = import_string(test_case_name)
                method = getattr(test_case, method_name)
                setattr(test_case, method_name, expectedFailure(method))

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
        dump_args = DatabaseClient.settings_to_cmd_args(self.connection.settings_dict)[1:]
        dump_cmd = ['cockroach', 'dump', source_database_name,
                    '--dump-mode=schema'] + dump_args
        load_args = DatabaseClient.settings_to_cmd_args(self.connection.settings_dict)[1:]
        load_cmd = ['cockroach', 'sql', '-d', target_database_name] + load_args

        with subprocess.Popen(dump_cmd, stdout=subprocess.PIPE) as dump_proc:
            with subprocess.Popen(load_cmd, stdin=dump_proc.stdout, stdout=subprocess.DEVNULL):
                # Allow dump_proc to receive a SIGPIPE if the load process exits.
                dump_proc.stdout.close()
