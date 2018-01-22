#!/bin/sh

sudo apt install -y python3 python3-pip
sudo pip3 install --upgrade pip

# Install MongoDB

if [ -z "`service --status-all | grep mongodb`" ]; then
    echo Install MongoDB
    sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 0C49F3730359A14518585931BC711F9BA15703C6
    sudo apt-get update
    sudo apt-get install -y mongodb
fi

# start MongoDB
sudo service mongodb start

# Install python packages

sudo pip3 install -r dependencies.txt

# Install NGINX

sudo apt-get install -y nginx
sudo service nginx start

#sudo ln -s $PWD/bvc_server.nginxconf /etc/nginx/sites-available/bvc_server
sudo cp -f bvc_server.nginxconf /etc/nginx/sites-available/default

# Install Gunicorn

sudo apt-get install -y gunicorn3

chmod +x *.sh
chmod u+x bin/gunicorn_start

# Install Supervisor

sudo aptitude install -y supervisor
