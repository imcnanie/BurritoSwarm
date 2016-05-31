#!/bin/bash

copters=$2

for i in `seq 1 $copters`;
do
    j=$(expr 14 + $i)
    #echo "udp://:${j}540@127.0.0.1:${j}557"
    
    roslaunch burrito hellacopters.launch copter_id:=$i &
    
done
