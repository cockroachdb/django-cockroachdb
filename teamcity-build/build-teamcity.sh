#!/usr/bin/env bash
set -x

# Set an environment variable used by cockroach/django/creation.py.
export RUNNING_COCKROACH_BACKEND_TESTS=1

# install the cockroach-django driver.
pip3 install psycopg2-binary
pip3 install .

# clone django into the repo.
git clone --depth 1 --single-branch --branch cockroach-2.2.x https://github.com/timgraham/django _django_repo

# install the django requirements.
cd _django_repo/tests/
pip3 install -e ..
pip3 install -r requirements/py3.txt
pip3 install -r requirements/postgres.txt

# download and start cockroach
wget "https://binaries.cockroachdb.com/cockroach-v19.2.0-rc.1.linux-amd64.tgz"
tar -xvf cockroach-v19.2*
cp cockroach-v19.2*/cockroach cockroach_exec
./cockroach_exec start --insecure &

# Bring in the settings needed to run the tests with cockroach.
cp ../../teamcity-build/cockroach_settings.py .

# Run the tests!
python3 ../../teamcity-build/runtests.py
