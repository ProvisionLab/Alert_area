#!/bin/sh

# Install MongoDB

sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv EA312927

sudo apt-get update

sudo apt-get install -y mongodb-org

# start MongoDB
sudo service mondodb start



# Install python packages

sudo apt-get install -y python3

pip3 install -r dependencies.txt


# Install Gunicorn

sudo apt-get install -y gunicorn3

chmod +x start.sh
chmod +x stop.sh
