#!/bin/bash
set -e

echo '1.mysql start ...'
echo `service mysql status`
service mysql start

echo '2.mysql init ...'
mysql < /init.sql

echo `service mysql status`
echo '3.InitComplete'

tail -f /dev/null
