#!/bin/bash

for i in $(ls reco_proc_*.pid 2>/dev/null) ; do

    echo stopping $i

    kill -SIGINT  `cat $i`
 
done

echo waiting...
sleep 2

for i in $(ls reco_proc_*.pid 2>/dev/null) ; do

    echo force kill $i

done

rm reco_proc_*.pid 2>/dev/null

exit 0
