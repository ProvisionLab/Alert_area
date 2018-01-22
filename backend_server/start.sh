#!/bin/sh


if [ -f bvc_server.pid ]; then
    echo it seems bvc server already is running.
    echo remove bvc_server.pid if it is not so.
    exit 1
fi

echo starting

# start MongoDB
sudo service mongodb start

sudo bin/gunicorn_start.bash
