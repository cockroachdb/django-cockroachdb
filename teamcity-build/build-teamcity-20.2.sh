#!/usr/bin/env bash
set -x

export RUN_GIS_TESTS=1
./teamcity-build/build-teamcity.sh "v20.2.6"
