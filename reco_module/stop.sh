#!/bin/bash

for i in $(ls reco_proc_*.pid) ; do

    echo stopping $i

    kill -HUP `cat $i`
    sleep 1

    kill `cat $i`
  
done

sleep 1

rm reco_proc_*.pid

for i in $(ls reco_proc_*.pid) ; do

    echo waiting $i

    while [ -f $i ]
    do
        sleep 1
    done
  
done

exit 0
