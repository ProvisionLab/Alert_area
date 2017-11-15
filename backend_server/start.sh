#!/bin/sh

# start MongoDB
sudo service mongodb start

# start as daemon
gunicorn3 bvc_server:app -b 0.0.0.0:5000 -p bvc_server.pid -D
