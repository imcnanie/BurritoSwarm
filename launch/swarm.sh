#!/bin/bash

copters=$1
for i in `seq 1 $copters`;
do
    j=$(expr 14 + $i)
    #echo "udp://:${j}540@127.0.0.1:${j}557"
    
    roslaunch mavros px4_swarm.launch fcu_url:="udp://:${j}540@127.0.0.1:${j}557" copter_id:="$i" &
    
done
