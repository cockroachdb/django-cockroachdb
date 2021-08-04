import os
import sys

# This file assumes it is being run in the django/tests/ repo.

shouldFail = False
res = os.system("python3 runtests.py --settings cockroach_settings -v 2")
if res != 0:
    shouldFail = True

res = os.system("python3 runtests.py gis_tests --settings cockroach_gis_settings -v 2")
if res != 0:
    shouldFail = True

sys.exit(int(shouldFail))
