#!/usr/bin/env bash
set -x

export USE_PSYCOPG2=1
./teamcity-build/build-teamcity.sh "v22.1.18"
