#!/bin/sh

# Install MongoDB

if [ -z "`service --status-all | grep mongodb`" ]
    echo Install MongoDB
    sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 0C49F3730359A14518585931BC711F9BA15703C6
    sudo apt-get update
    sudo apt-get install -y mongodb
fi

# start MongoDB
sudo service mondodb start


# Install python packages

sudo apt-get install -y python3

pip3 install -r dependencies.txt


# Install Gunicorn

sudo apt-get install -y gunicorn3

chmod +x start.sh
chmod +x stop.sh
