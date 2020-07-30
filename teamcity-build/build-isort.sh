#!/usr/bin/env bash
set -x
pip3 install isort
cd django_cockroachdb
python3 -m isort --check-only --diff .
