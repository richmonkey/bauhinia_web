#!/bin/bash
#!/bin/bash

uwsgi=/usr/local/python2.7/bin/uwsgi
home=/usr/local/python2.7
app_dir=/vagrant/dev/im_api

$uwsgi --uid nobody --gid nobody --chdir $app_dir --http :6000 -M  -p 1 -w im --callable app -t 60 --max-requests 5000 --vacuum --home $home --daemonize /tmp/bauhinia_api.log --pidfile /tmp/bauhinia_api.pid --touch-reload /tmp/bauhinia_api.touch

$uwsgi --uid nobody --gid nobody --chdir $app_dir --http :6001 --gevent 1000 -M -p 1 -w webapp  -t 60 --max-requests 5000 --vacuum --home $home --daemonize /tmp/bauhinia_web.log --pidfile /tmp/bauhinia_web.pid --touch-reload /tmp/bauhinia_web.touch

$uwsgi --uid nobody --gid nobody --chdir $app_dir --http :6002 --gevent 1000 -M  -p 1 -w qr_login  -t 60 --max-requests 5000 --vacuum --home $home --daemonize /tmp/qr_login.log --pidfile /tmp/qr_login.pid --touch-reload /tmp/qr_login.touch

$uwsgi --uid nobody --gid nobody --chdir $app_dir --http :6003 -M  -p 1 -w im --callable app --pyargv "face" -t 60 --max-requests 5000 --vacuum --home $home --daemonize /tmp/face_api.log --pidfile /tmp/face_api.pid --touch-reload /tmp/face_api.touch
