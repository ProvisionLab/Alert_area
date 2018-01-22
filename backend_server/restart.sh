#!/bin/bash

if [ -f bvc_server.pid ] ; then

  echo restarting...

  sudo kill -HUP `cat bvc_server.pid`

else
    echo no runing server found
fi
