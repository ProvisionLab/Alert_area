#!/bin/sh

if [ -f bvc_server.pid ] ; then

  echo stoping...

  sudo kill -HUP `cat bvc_server.pid`
  sudo kill `cat bvc_server.pid`

  #rm bvc_server.pid

  while [ -f bvc_server.pid ]
  do
    sleep 1
  done

#  exit 0

else

  echo no runing server found
#  exit 1

fi

if [ -f bvc_server2.pid ] ; then

  echo stoping 2 ...

  sudo kill -HUP `cat bvc_server2.pid`
  sudo kill `cat bvc_server2.pid`

  #rm bvc_server2.pid

  while [ -f bvc_server2.pid ]
  do
    sleep 1
  done

#  exit 0

fi
