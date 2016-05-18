import roslib
import rospy
import std_msgs

from threading import Thread

import time
import ast
import os

import velocity_goto

class artoo:
    def __init__(self):
        self.stick_map = []

        self.x_offset = 0.0
        self.y_offset = 0.0
        self.z_offset = 0.0

        self.butt = ""

    def handle_sticks(self, msg):
        unpack = ast.literal_eval(str(msg)[6:])

        self.stick_map = []

        for i in unpack:
           self.stick_map.append(float(int(i)-1500)/500)

        self.x_offset = self.stick_map[1]
        self.y_offset = -self.stick_map[2]
        self.z_offset = self.stick_map[0]

    def handle_buttons(self, msg):
        self.butt = msg

    def start_subbing(self):
        stick_sub = rospy.Subscriber("sticks", std_msgs.msg.String, self.handle_sticks)
        button_sub = rospy.Subscriber("unused_buttons", std_msgs.msg.String, self.handle_buttons)


print "initializing copter..."

cop = velocity_goto.posVel(copter_id = "1")

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

a = artoo()
a.start_subbing()

while True:
    print a.stick_map

    cop.set_velocity(a.x_offset, a.y_offset, a.z_offset)

    #time.sleep(0.025)

