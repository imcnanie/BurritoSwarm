import roslib
import rospy
import std_msgs

from math import *
from threading import Thread

import time
import ast
import os

import velocity_goto

class artoo:
    def __init__(self):
        self.stick_map = []

        self.mod_scalar = 0.00001

        self.x_offset = 0.0
        self.y_offset = 0.0
        self.z_offset = 0.0

        self.fin_x = 0.0
        self.fin_y = 0.0
        self.fin_z = 0.0

        self.butt = ""

    def handle_sticks(self, msg):
        unpack = ast.literal_eval(str(msg)[6:])

        self.stick_map = []

        for i in unpack:
            self.stick_map.append(float(int(i)-1500)/500)

        self.x_offset = self.stick_map[1] * self.mod_scalar
        self.y_offset = -self.stick_map[2] * self.mod_scalar
        self.z_offset = self.stick_map[0]

        self.fin_x = self.fin_x + self.stick_map[1]
        self.fin_y = self.fin_y - self.stick_map[2]
        self.fin_z = self.fin_z + self.stick_map[0]

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

a.fin_x = cop.cur_pos_x
a.fin_y = cop.cur_pos_y
a.fin_z = cop.cur_alt

while True:
    #print cop.final_pos_x, "--x-->", cop.cur_pos_x
    #print cop.final_pos_y, "--y-->", cop.cur_pos_y
    #print cop.final_alt, "--z-->", cop.cur_alt

    print a.stick_map

    print a.x_offset, "   -   ", a.y_offset

    cop.update(a.fin_x, a.fin_y, a.fin_z)

    if abs(a.x_offset) < 0.01 and abs(a.y_offset) < 0.01 and abs(a.z_offset) < 0.01:
        a.fin_x = cop.cur_pos_x
        a.fin_y = cop.cur_pos_y
        a.fin_z = cop.cur_alt

    #time.sleep(0.025)

