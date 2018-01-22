#!/bin/bash

NAME="bvc_server" 

APPDIR=/home/ubuntu/BVC/backend_server
LOGDIR=$APPDIR/logs

SOCKFILE=$APPDIR/run/gunicorn.sock 

RUNDIR=$(dirname $SOCKFILE)
test -d $RUNDIR || mkdir -p $RUNDIR

# start as daemon, SSL
gunicorn3 main:app \
    --name $NAME \
    --bind=unix:$SOCKFILE \
    --pid $NAME.pid -D \
    --access-logfile $LOGDIR/bvc_access.log \
    --log-file $LOGDIR/$NAME.log  \
    --log-level info
