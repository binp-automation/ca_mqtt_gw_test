#!/bin/bash

source ./script/epics_env.sh &&
cd epics-base &&
make &&
cd .. &&
echo "epics built successfully"
