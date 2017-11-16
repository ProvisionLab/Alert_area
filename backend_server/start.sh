#!/bin/sh

if [ ! -f bvc_server.pid ]; then

echo starting...

# start as daemon
gunicorn3 bvc_server:app -b 0.0.0.0:5000 -p bvc_server.pid -D


fi
