#!/usr/bin/env python
import roslib
import rospy
from nav_msgs.msg import Odometry
from sensor_msgs.msg import NavSatFix
import std_msgs
import mavros
import mavros_msgs.srv
from mavros import command

from threading import Thread

import time
import os

import velocity_goto
import buttonHandler

def postMode(modeID):
    if True:
        set_mode = rospy.ServiceProxy('/mavros/copter1/set_mode', mavros_msgs.srv.SetMode)
        ret = set_mode(base_mode=0, custom_mode=modeID)
        print "Changing modes to",modeID,": ", ret
        time.sleep(0.1)

bpub = rospy.Publisher('abpause_buttons', std_msgs.msg.String, queue_size=10)
rospy.init_node('talker', anonymous=True)

bh = buttonHandler.buttonHandler()
bh.startListening()

while True:
    if bh.changed():
        #print bh.buttonState

        if bh.buttonState["A"][1] == "Short" and bh.buttonState["B"][1] == "Short" and bh.buttonState["Loiter"][1] == "Short":
            print "ABORT"
            bpub.publish(std_msgs.msg.String("ABORT"))
	if bh.buttonState["Preset1"][1] == "Short":
            print "MANUAL"
            postMode("MANUAL")
	if bh.buttonState["Fly"][1] == "Short":
            print "POSCTL"
            postMode("POSCTL")

    try:
        pass
    except KeyboardInterrupt:
        bh.destroy = True
        time.sleep(0.5)
        break

