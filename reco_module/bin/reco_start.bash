#!/bin/bash

NAME="reco" 
RECO_WORKERS=4

APPDIR=/home/ubuntu/BVC/reco_module
LOGDIR=$APPDIR/logs

cd $APPDIR

exec python3 reco_main.py -w $RECO_WORKERS
