#!/bin/bash

python3 ./script/prepare_env.py
python3 ./script/prepare_ioc.py
./script/prepare_test.sh
