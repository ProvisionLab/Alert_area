#!/bin/bash

NAME="bvc_server" 

APPDIR=/home/ubuntu/BVC/backend_server
LOGDIR=$APPDIR/logs

SOCKFILE=$APPDIR/run/gunicorn.sock 

cd $APPDIR

RUNDIR=$(dirname $SOCKFILE)
test -d $RUNDIR || mkdir -p $RUNDIR

# start as daemon, SSL
exec gunicorn3 main:app \
    --name $NAME \
    --bind=unix:$SOCKFILE \
    --access-logfile $LOGDIR/bvc_access.log \
    --log-file $LOGDIR/$NAME.log  \
    --log-level debug

#    --log-level info
#    --pid $NAME.pid -D \
