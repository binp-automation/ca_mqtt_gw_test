#!/bin/bash

source ./script/epics_env.sh &&
python3 ./script/prepare_ioc.py &&
cd ./epicsTestApp &&
make &&
cd .. &&
echo "ioc built successfully"