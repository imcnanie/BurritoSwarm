#!/usr/bin/env python

import subprocess
import signal
import rospy
import sys
import os

rospy.init_node('swarm_mavros')

try:
    copters = int(sys.argv[1])
except:
    copters = 1
pros = []

for i in range(copters):
    j = str(i + 15)

    cmd = "roslaunch burrito px4_swarm.launch fcu_url:=\"udp://:"+j+"540@:"+j+"557\" copter_id:=\""+str(i+1)+"\""
    print "THE COMMAND", cmd
    pro = subprocess.Popen(cmd, stdout=subprocess.PIPE, 
                       shell=True, preexec_fn=os.setsid) 
    pros.append(pro)


while not rospy.is_shutdown():
    pass #print "swarm_mavros.py is good"

for pro in pros:
    try:
	print "Killing"
        #pro.kill()
        os.killpg(os.getpgid(pro.pid), signal.SIGTERM)
    except:
        print "failed to kill copters"
