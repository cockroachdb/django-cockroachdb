#!/usr/bin/env bash
set -x
pip3 install isort
cd cockroach
python3 -m isort --recursive --check-only --diff
