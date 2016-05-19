#!/usr/bin/env python

# Kill all the flying copters, might want to call the police if this happens...

import roslib
import rospy
import std_msgs

from threading import Thread

import time
import ast
import os

import velocity_goto

is_test = False

if True:
    rospy.init_node("killer")
    print "initializing copter..."

    cop = velocity_goto.posVel(copter_id = "1")


if is_test:
    
    cop.start_subs()
    time.sleep(1.0)

    cop.subscribe_pose_thread()
    time.sleep(0.1)
    
    cop.start_navigating()
    time.sleep(0.1)

    cop.setmode(custom_mode = "OFFBOARD")
    cop.arm()
    time.sleep(0.1)

    cop.takeoff_velocity()

print "ready"

if is_test:
    cop.update(1000,1000,10)

    print "KILL? (y/n): ",
    key = raw_input()

while True:
    cop.disarm()
    time.sleep(1.0)        

    break
