#!/usr/bin/env python
import roslib
import rospy
from nav_msgs.msg import Odometry
from sensor_msgs.msg import NavSatFix
import std_msgs
import mavros
import mavros_msgs.srv
import mavros_msgs
from mavros import command

from threading import Thread

import time
import os

import velocity_goto
#import pixrc
#import rc_flasher

mav_sticks = ()
org_sticks = []
unorg_sticks_list = []

for i in range(8):
    org_sticks.append(0)
    unorg_sticks_list.append(0)

def handle_sticks(msg):
    global mav_sticks
    global org_sticks
    global unorg_sticks_list

    mav_sticks = msg.channels

    unorg_sticks_list = [o for o in mav_sticks]

    org_sticks[2] = unorg_sticks_list[1]
    org_sticks[1] = unorg_sticks_list[0]
    org_sticks[0] = unorg_sticks_list[2]
    for i in range(3,8):
        org_sticks[i] = unorg_sticks_list[i]

def postMode(modeID):
    if True:
        set_mode = rospy.ServiceProxy('/mavros/set_mode', mavros_msgs.srv.SetMode)
        ret = set_mode(base_mode=0, custom_mode=modeID)
        print "Changing modes to",modeID,": ", ret
        time.sleep(0.1)

bpub = rospy.Publisher('sticks', std_msgs.msg.String, queue_size=10)
rospy.init_node('talker', anonymous=True)
rate = rospy.Rate(30)

mav_stick_sub = rospy.Subscriber("/mavros/copter1/rc/in", mavros_msgs.msg.RCIn, handle_sticks)

#rc = pixrc.controller()

#rc_flasher.flash()

time.sleep(1.0)

while True:
    #print rc.rcChansOut

    #sticks_list = str(rc.rcChansOut)

    #sticks_list = str(mav_sticks[mav_sticks.index("["):])

    #unorg_sticks_list = str([i for i in mav_sticks])

    sticks_list = str(org_sticks)

    if sticks_list[1] == "0":
        sticks_list = "[1500, 1500, 1500, 1500]"
        #print "FAILSAFE -----------", rc.rcChansOut

    print sticks_list

    bpub.publish(std_msgs.msg.String(sticks_list))

    rate.sleep()

    try:
        pass
    except KeyboardInterrupt:
        time.sleep(0.5)
        break
