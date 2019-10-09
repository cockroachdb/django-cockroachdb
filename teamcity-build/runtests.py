import os
import sys

# This file assumes it is being run in the django/tests/ repo.

# edit this list to include more test apps in the CI.
enabled_test_apps = [
    'admin_ordering',
    'basic',
    'db_functions.comparison',
    'db_functions.text',
    'delete_regress',
    'indexes',
    'many_to_one',
    'model_fields',
    'ordering',
    'reserved_names',
    'update',
]

run_tests_cmd = "python3 runtests.py %s --settings cockroach_settings --parallel 1 -v 2"

shouldFail = False
for app_name in enabled_test_apps:
    res = os.system(run_tests_cmd % app_name)
    if res != 0:
        shouldFail = True
sys.exit(1 if shouldFail else 0)
