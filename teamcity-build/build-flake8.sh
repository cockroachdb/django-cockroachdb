#!/usr/bin/env bash
set -x
pip3 install flake8
cd django_cockroachdb
python3 -m flake8
