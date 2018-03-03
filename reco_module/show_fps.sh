#!/bin/bash

TOTAL=0

for f in $(ls reco_proc_*.pid) ; do

    reco_id=`echo $f | cut -d '_' -f 3 | cut -d '.' -f 1`

    if [ -f reco_$reco_id.log ]; then

        FPS=`grep "total FPS" reco_$reco_id.log | tail -n 1 | cut -d ' ' -f 7 | cut -d '/' -f 2`

        if [ -z "$FPS" ]; then
            FPS=0
        fi
    
        echo "[$reco_id] fps: $FPS"

        TOTAL=`python -c "print($TOTAL + $FPS)" 2>/dev/null`
    fi

done

echo Total FPS: $TOTAL
