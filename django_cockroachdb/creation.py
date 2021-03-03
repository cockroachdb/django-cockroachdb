import os
from unittest import expectedFailure, skip

from django.conf import settings
from django.db.backends.postgresql.creation import (
    DatabaseCreation as PostgresDatabaseCreation,
)
from django.utils.module_loading import import_string


class DatabaseCreation(PostgresDatabaseCreation):

    def mark_expected_failures_and_skips(self):
        """
        Marks tests in Django's test suite which are expected failures on this
        database and tests which should be skipped on this database.
        """
        for test_name in self.connection.features.django_test_expected_failures:
            test_case_name, _, test_method_name = test_name.rpartition('.')
            test_app = test_name.split('.')[0]
            # Importing a test app that isn't installed raises RuntimeError.
            if test_app in settings.INSTALLED_APPS:
                test_case = import_string(test_case_name)
                test_method = getattr(test_case, test_method_name)
                setattr(test_case, test_method_name, expectedFailure(test_method))
        for reason, tests in self.connection.features.django_test_skips.items():
            for test_name in tests:
                test_case_name, _, test_method_name = test_name.rpartition('.')
                test_app = test_name.split('.')[0]
                # Importing a test app that isn't installed raises RuntimeError.
                if test_app in settings.INSTALLED_APPS:
                    test_case = import_string(test_case_name)
                    test_method = getattr(test_case, test_method_name)
                    setattr(test_case, test_method_name, skip(reason)(test_method))

    def create_test_db(self, *args, **kwargs):
        # This environment variable is set by teamcity-build/runtests.py or
        # by a developer running the tests locally.
        if os.environ.get('RUNNING_COCKROACH_BACKEND_TESTS'):
            self.mark_expected_failures_and_skips()
        super().create_test_db(*args, **kwargs)

    def _clone_test_db(self, suffix, verbosity, keepdb=False):
        raise NotImplementedError(
            "CockroachDB doesn't support cloning databases. "
            "Disable the option to run tests in parallel processes."
        )
