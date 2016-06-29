from nav_msgs.msg import Odometry
import std_msgs
import rosnode
import roslib
import rospy
import tf

from threading import Thread
from math import *
import time
import ast
import os

import velocity_goto
import count_copters

class artoo:
    def __init__(self):
        self.stick_map = []

        self.mod_scalar = 1.0 #careful

        self.x_offset = 0.0
        self.y_offset = 0.0
        self.z_offset = 0.0

        self.fin_x = 0.0
        self.fin_y = 0.0
        self.fin_z = 0.0

        for i in range(8):
            self.stick_map.append(0.0)

    def handle_sticks(self, msg):
        unpack = ast.literal_eval(str(msg)[6:])

        raw_stick = []

        for i in unpack:
            raw_stick.append(float(int(i)-1500)/500)

        try:
            for r in range(8):
                self.stick_map[r] = raw_stick[r]
        except:
            pass

        self.x_offset = self.x_offset + self.stick_map[1] * self.mod_scalar
        self.y_offset = self.y_offset - self.stick_map[2] * self.mod_scalar
        self.z_offset = self.stick_map[0]

    def start_subbing(self):
        stick_sub = rospy.Subscriber("sticks", std_msgs.msg.String, self.handle_sticks)

cop_num = count_copters.count_copters()

rospy.init_node("copter_broadcast_frames")

print "initializing copter..."

cops = []

for i in range(cop_num):
    print "STR", str(i+1)
    cops.append(velocity_goto.posVel(copter_id = str(i+1)))

for cop in cops:
    cop.start_subs()
    time.sleep(0.25)

    cop.subscribe_pose_thread()
    time.sleep(0.1)

    cop.start_navigating()
    time.sleep(0.1)


a = artoo()
a.start_subbing()

home_x = cops[0].cur_pos_x
home_y = cops[0].cur_pos_y
home_z = cops[0].cur_alt

a.fin_x = home_x
a.fin_y = home_y
a.fin_z = home_z

center_x = home_x
center_y = home_y

offs_x = []
offs_y = []
offs_r = 1.0 + float(cop_num)
offs_yaw = 0.0

io = 0

if True:
    for cop in cops:
        cop_fraction = float(io) / float(cop_num)
        cop_radian = (pi*2.0) * cop_fraction

        offs_x.append(cos(cop_radian)*offs_r)
        offs_y.append(sin(cop_radian)*offs_r)

        io = io + 1

print "taking off"
velocity_goto.SafeTakeoff(cops, offs_x, offs_y, alt = 10.0)

print "ready"

while True:
    io = 0

    for cop in cops:
        cop_fraction = float(io) / float(cop_num)
        cop_radian = (pi*2.0) * cop_fraction - (offs_yaw/125.0)

        cop_deg = cop_radian * 180.0/pi 
        cop_deg = (cop_deg + 36000.0) % 360

        cop_radian = float(cop_deg) / (180.0/pi) 

        offs_yaw = offs_yaw + a.stick_map[3]

        offs_r = offs_r + 0.0 #(a.stick_map[7]+2.0) #breaks sometimes

        print "STICK_MAP", a.stick_map[7]

        offs_x[io] = cos(cop_radian)*offs_r
        offs_y[io] = sin(cop_radian)*offs_r

        a.fin_x = center_x + offs_x[io]
        a.fin_y = center_y + offs_y[io] 

        a.fin_z = 10.0 + io*1.2 #staggering

        cop.update(a.fin_x + a.x_offset, a.fin_y + a.y_offset, a.fin_z)

        time.sleep(0.1)

        io = io + 1 

    #time.sleep(0.025)

