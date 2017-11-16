#!/bin/sh

if [ -f bvc_server.pid ]; then

echo stoping...

kill -HUP `cat bvc_server.pid`
kill `cat bvc_server.pid`

rm bvc_server.pid

fi

