#!/bin/bash

source ./script/epics_env.sh &&
source ./venv3/bin/activate &&
python3 ./script/test_all.py
