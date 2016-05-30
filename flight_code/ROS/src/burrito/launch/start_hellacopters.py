#!/usr/bin/env python

import subprocess
import signal
import rospy
import sys
import os

rospy.init_node('start_hellacopters')

try:
    copters = int(sys.argv[1])
except:
    copters = 1
pros = []


for i in range(copters):
    j = str(i + 14)

    cmd = "roslaunch burrito hellacopters.launch copter_id:="+str(i+1)
    pro = subprocess.Popen(cmd, stdout=subprocess.PIPE, 
                       shell=True, preexec_fn=os.setsid) 
    pros.append(pro)

while not rospy.is_shutdown():
    pass #print "swarm_mavros.py is good"

for pro in pros:
    os.killpg(os.getpgid(pro.pid), signal.SIGTERM)

