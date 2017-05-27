#!/bin/sh
set -ex
mkdir rsyslog-dev
docker-compose up -d rsyslog
