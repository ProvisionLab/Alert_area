#!/bin/sh

if [ ! -f bvc_server.pid ]; then
    echo no runing server found
    exit 1
fi

echo stoping...

kill -HUP `cat bvc_server.pid`
kill `cat bvc_server.pid`

#rm bvc_server.pid

while [ -f bvc_server.pid ]
do
  sleep 1
done

exit 0
