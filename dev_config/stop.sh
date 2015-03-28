#!/bin/bash
uwsgi=/usr/local/python2.7/bin/uwsgi

$uwsgi --stop /tmp/bauhinia_api.pid
$uwsgi --stop /tmp/bauhinia_web.pid
$uwsgi --stop /tmp/qr_login.pid
