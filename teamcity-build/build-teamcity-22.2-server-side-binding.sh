#!/usr/bin/env bash
set -x

export USE_SERVER_SIDE_BINDING=1
./teamcity-build/build-teamcity.sh "v22.2.7"
