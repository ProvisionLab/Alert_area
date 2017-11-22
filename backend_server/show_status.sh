#!/bin/sh

RECO_PID=`pgrep -f reco_main`

if [ -z "$RECO_PID" ]; then
    echo no reco_main process was found
    exit 1
fi

echo ==== CPU ================
top -bn1 -p $RECO_PID

echo ==== GPU ================
nvidia-smi pmon --count 4
