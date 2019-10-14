#!/usr/bin/env bash
set -x
pip3 install flake8
cd cockroach
python3 -m flake8
