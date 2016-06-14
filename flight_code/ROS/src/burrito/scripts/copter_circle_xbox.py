from nav_msgs.msg import Odometry
from sensor_msgs.msg import Joy

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

import copter_control

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
        try:
            for r in range(0,8):
                self.stick_map[r] = msg.axes[r]/32000.0
        except:
            pass

    def start_subbing(self):
        stick_sub = rospy.Subscriber("/joy", Joy, self.handle_sticks)

rospy.init_node("copter_circle_xbox")

print "initializing copters..."

cc = copter_control.CopterControl()

a = artoo()
a.start_subbing()

home_x = cc.cops_odom[0]['sub'].home_lat
home_y = cc.cops_odom[0]['sub'].home_lon
home_z = cc.cops_odom[0]['sub'].home_alt

a.fin_x = home_x
a.fin_y = home_y
a.fin_z = home_z

center_x = home_x
center_y = home_y

offs_x = []
offs_y = []
offs_r = 5.0 + float(cc.num_cops)
offs_yaw = 0.0

io = 0

if True:
    for cop in cc.cops_odom:
        cop_fraction = float(io) / float(cc.num_cops)
        cop_radian = (pi*2.0) * cop_fraction

        offs_x.append(cos(cop_radian)*offs_r)
        offs_y.append(sin(cop_radian)*offs_r)

        io = io + 1

initial_coords = []
for x in range(len(offs_x)):
    initial_coords.append((offs_x[x],offs_y[x]))

print "taking off", cc.num_cops, "copters"

st = cc.safe_takeoff(initial_coords, alt = 10.0)

print "ready"

while True:
    io = 0

    for cop in cc.cops_odom:
	a.x_offset = a.x_offset + a.stick_map[2] * a.mod_scalar
        a.y_offset = a.y_offset - a.stick_map[3] * a.mod_scalar
        a.z_offset = a.stick_map[1]

        cop_fraction = float(io) / float(cc.num_cops)
        cop_radian = (pi*2.0) * cop_fraction - (offs_yaw/125.0)

        cop_deg = cop_radian * 180.0/pi 
        cop_deg = (cop_deg + 36000.0) % 360

        cop_radian = float(cop_deg) / (180.0/pi) 

        offs_yaw = offs_yaw + a.stick_map[0]

        #offs_r = offs_r + (a.stick_map[7]+2.0) #breaks sometimes

        offs_x[io] = cos(cop_radian)*offs_r
        offs_y[io] = sin(cop_radian)*offs_r

        a.fin_x = center_x + offs_x[io]
        a.fin_y = center_y + offs_y[io] 
	
        a.fin_z = 10.0 + io*1.2 #staggering

        print cop

        cc.publish_odom(cop['pub'], a.fin_x + a.x_offset, a.fin_y + a.y_offset, a.fin_z, prefix = cop['prefix'])
	#print "yaw: " + str(offs_yaw)
	#print "x: " + str(a.x_offset)
	#print "y: " + str(a.y_offset)
        time.sleep(0.1)

        io = io + 1 

    #time.sleep(0.025)

