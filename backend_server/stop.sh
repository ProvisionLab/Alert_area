#!/bin/sh

kill -HUP `cat bvc_server.pid`
kill `cat bvc_server.pid`

