from django.db.backends.postgresql.creation import (
    DatabaseCreation as PostgresDatabaseCreation,
)


class DatabaseCreation(PostgresDatabaseCreation):

    def _clone_test_db(self, suffix, verbosity, keepdb=False):
        raise NotImplementedError(
            "CockroachDB doesn't support cloning databases. "
            "Disable the option to run tests in parallel processes."
        )
