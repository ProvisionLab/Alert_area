#!/bin/bash

if [ -f bvc_server.pid ] ; then

  echo stoping...

  sudo kill -TERM `cat bvc_server.pid`

  COUNTER=0

  while [ -f bvc_server.pid ] ; do

      sleep 2

      COUNTER=$[COUNTER + 2]

      echo waiting $COUNTER

      if [ "30" -lt "$COUNTER" ] ; then
        #sudo kill -INT `cat bvc_server.pid`
        sudo rm bvc_server.pid
        break
      fi

  done

  exit 0

else

  echo no runing server found
  exit 1

fi
