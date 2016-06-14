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

import pixrc

import rc_flasher

def postMode(modeID):
    if True:
        set_mode = rospy.ServiceProxy('/mavros/set_mode', mavros_msgs.srv.SetMode)
        ret = set_mode(base_mode=0, custom_mode=modeID)
        print "Changing modes to",modeID,": ", ret
        time.sleep(0.1)

bpub = rospy.Publisher('sticks', std_msgs.msg.String, queue_size=10)
rospy.init_node('talker', anonymous=True)
rate = rospy.Rate(30)

rc = pixrc.controller()

rc_flasher.flash()

while True:
    #print rc.rcChansOut

    sticks_list = str(rc.rcChansOut)

    if sticks_list[1] == "0":
        sticks_list = "[1500, 1500, 1500, 1500]"
        print "FAILSAFE -----------", rc.rcChansOut

    print sticks_list

    bpub.publish(std_msgs.msg.String(sticks_list))

    rate.sleep()

    try:
        pass
    except KeyboardInterrupt:
        time.sleep(0.5)
        break
