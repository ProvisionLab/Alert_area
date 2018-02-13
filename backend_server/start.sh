#!/bin/sh


# start MongoDB
sudo service mongodb start

# start gunicorn
sudo supervisorctl start bvc_server
