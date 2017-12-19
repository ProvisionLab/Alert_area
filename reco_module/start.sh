#!/bin/bash


export RECO_TOTAL_PROCS=4
#export RECO_TOTAL_PROCS=2

for i in $(seq $RECO_TOTAL_PROCS) ; do
    #RECO_PROC_ID=$i python3 reco_main.py &
    RECO_PROC_ID=$i python3 reco_main.py 2>/dev/null &
done
