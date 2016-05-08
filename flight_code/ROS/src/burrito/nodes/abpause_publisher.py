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

limit = 99

def postMode(modeID, copid):
    if True:
        service_cop = '/mavros/' + copid + '/set_mode'
        set_mode = rospy.ServiceProxy(service_cop, mavros_msgs.srv.SetMode)
        ret = set_mode(base_mode=0, custom_mode=modeID)
        print "Changing modes to",modeID,": ", ret
        time.sleep(0.1)

def killCop(copid):
    if True:
        service_cop = '/mavros/' + copid + '/cmd/arming'
        arm = rospy.ServiceProxy(service_cop, mavros_msgs.srv.CommandBool)
        print "Disarming: ", arm(False)

bpub = rospy.Publisher('abpause_buttons', std_msgs.msg.String, queue_size=10)
rospy.init_node('talker', anonymous=True)

bh = buttonHandler.buttonHandler()
bh.startListening()

while True:
    if bh.changed():
        if bh.buttonState["A"][1] == "Short" and bh.buttonState["B"][1] == "Short" and bh.buttonState["Loiter"][1] == "Short":
            print "ABORT"
            bpub.publish(std_msgs.msg.String("ABORT"))
            for i in range(limit):
                copid = 'copter' + str(i+1)
                killCop(copid)

	if bh.buttonState["Preset1"][1] == "Short":
            print "MANUAL"
            for i in range(limit):
                copid = 'copter' + str(i+1)
                postMode("MANUAL", copid)

	if bh.buttonState["Fly"][1] == "Short":
            print "POSCTL"
            for i in range(limit):
                copid = 'copter' + str(i+1)
                postMode("POSCTL", copid)

    try:
        pass
    except KeyboardInterrupt:
        bh.destroy = True
        time.sleep(0.5)
        break

