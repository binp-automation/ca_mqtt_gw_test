#!/bin/bash

cd mosquitto &&
make WITH_TLS=no WITH_DOCS=no &&
cd .. &&
echo "mosquitto built successfully"
