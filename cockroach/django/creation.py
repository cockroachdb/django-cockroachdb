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
            'db_functions.comparison.test_cast.CastTests.test_cast_from_db_datetime_to_date_group_by',
            # CAST timestamptz to time doesn't respect active time zone:
            # https://github.com/cockroachdb/cockroach-django/issues/37
            'db_functions.comparison.test_cast.CastTests.test_cast_from_db_datetime_to_time',
            # DATE_TRUNC result is incorrectly localized when a timezone is set:
            # https://github.com/cockroachdb/cockroach-django/issues/32
            'many_to_one.tests.ManyToOneTests.test_select_related',
            'multiple_database.tests.QueryTestCase.test_basic_queries',
            'reserved_names.tests.ReservedNameTests.test_dates',
            # POWER() doesn't support negative exponents:
            # https://github.com/cockroachdb/cockroach-django/issues/22
            'db_functions.math.test_power.PowerTests.test_integer',
            # Tests that assume a serial pk: https://github.com/cockroachdb/cockroach-django/issues/18
            'ordering.tests.OrderingTests.test_order_by_fk_attname',
            'ordering.tests.OrderingTests.test_order_by_pk',
            # Transaction issues: https://github.com/cockroachdb/cockroach-django/issues/14
            'basic.tests.SelectOnSaveTests.test_select_on_save_lying_update',
            'delete_regress.tests.DeleteLockingTest.test_concurrent_delete',
            # No support for NULLS FIRST/LAST: https://github.com/cockroachdb/cockroach-django/issues/17
            'admin_ordering.tests.TestAdminOrdering.test_specified_ordering_by_f_expression',
            'ordering.tests.OrderingTests.test_default_ordering_by_f_expression',
            'ordering.tests.OrderingTests.test_order_by_nulls_first',
            'ordering.tests.OrderingTests.test_order_by_nulls_last',
            'ordering.tests.OrderingTests.test_orders_nulls_first_on_filtered_subquery',
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
