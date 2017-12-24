#!/bin/bash

#export RECO_TOTAL_PROCS=4
export RECO_TOTAL_PROCS=2


if [ ! -z "$(ls reco_proc_*.pid 2>/dev/null)" ] ; then

    echo recognizers already are runing...
    exit 1

fi

echo starting $RECO_TOTAL_PROCS recognizing processes

for i in $(seq $RECO_TOTAL_PROCS) ; do
    #RECO_PROC_ID=$i python3 reco_main.py &
    RECO_PROC_ID=$i python3 reco_main.py 2>/dev/null &
done

sleep 2

echo .
