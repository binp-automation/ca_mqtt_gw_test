# CA_MQTT_GW Testing environment

[![Travis CI][travis_badge]][travis]
[![License][license_badge]][license]

[travis_badge]: https://api.travis-ci.org/binp-automation/ca_mqtt_gw_test.svg
[license_badge]: https://img.shields.io/github/license/binp-automation/ca_mqtt_gw_test.svg

[travis]: https://travis-ci.org/nthend/ringbuf
[license]: https://github.com/binp-automation/ca_mqtt_gw_test/blob/master/LICENSE

## Required packages
+ make
+ python3
+ python2
+ python-virtualenv
+ libpython2-dev
+ libreadline-dev
+ libc-ares-dev
+ uuid-dev
+ python-qt4

## Usage
```bash
git clone https://github.com/binp-automation/ca_mqtt_gw_test.git
git submodule update --init

./prepare.sh
./build.sh

./test.sh
```
