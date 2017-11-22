#!/bin/sh

if [ -f bvc_server.pid ]; then
    echo it seems bvc server already is running.
    echo remove bvc_server.pid if it is not so.
    exit 1
fi

echo starting

# start as daemon
gunicorn3 bvc_server:app -b 0.0.0.0:5000 -p bvc_server.pid -D \
    --access-logfile bvc_access.log \
    --log-file bvc_server.log  \
    --log-level info
