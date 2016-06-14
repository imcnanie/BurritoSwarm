from nav_msgs.msg import Odometry
import std_msgs
import rosnode
import roslib
import rospy
import tf

from threading import Thread
from math import *
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Point, Quaternion
from sensor_msgs.msg import NavSatFix
from std_msgs.msg import Bool
import random
import time
import ast
import os

import copter_control

class artoo:
    def __init__(self):
        self.stick_map = []

        self.mod_scalar = 1.0

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

        self.x_offset = self.stick_map[1] * self.mod_scalar
        self.y_offset = -self.stick_map[2] * self.mod_scalar
        self.z_offset = self.stick_map[0]

    def start_subbing(self):
        stick_sub = rospy.Subscriber("sticks", std_msgs.msg.String, self.handle_sticks)

class buttons:
    def __init__(self):
        self.click = ""

    def handle_buttons(self, msg):
        self.click = str(msg)[6:]

    def start_subbing(self):
        button_sub = rospy.Subscriber("unused_buttons", std_msgs.msg.String, self.handle_buttons)

rospy.init_node("copter_broadcast_frames")

print "Please wait while the copters warm up..."

cc = copter_control.CopterControl()

cops_odom = [] 
cops = ["/copter"+str(x+1)+"/" for x in range(cc.num_cops)]

for prefix in cops:
    pub = rospy.Publisher(prefix+'hellacopters/setpoint_odom/cmd_odom',
                          Odometry,
                          queue_size = 10)
    sub = cc.Subscribers()
    rospy.Subscriber(prefix+'mavros/global_position/local',
                     Odometry,
                     sub.handle_pose)
    rospy.Subscriber(prefix+'hellacopters/home_pos',
                     Odometry,
                     sub.handle_home)
    rospy.Subscriber(prefix+'hellacopters/setpoint_odom/reached',
                     Bool,
                     sub.handle_reached)

    cops_odom.append({"prefix":prefix, "pub":pub, "sub":sub})

offs_x = [0.0, -6.5, -6.5, 6.5, 6.5]
offs_y = [0.0, 2.5, -2.5, 2.5, -2.5]
offs_alt = [0.0, 30.0, 50.0, 30.0, 50.0]

adj_offs_y = [0.0, 0.0, 0.0, 0.0, 0.0]

initial_coords = []
for x in range(len(offs_x)):
    initial_coords.append((offs_x[x],offs_y[x]))

st = cc.safe_takeoff(initial_coords)

time.sleep(1.0)

b = buttons()
b.start_subbing()

a = artoo()
a.start_subbing()

a.fin_x = cops_odom[0]["sub"].cur_pos_x
a.fin_y = cops_odom[0]["sub"].cur_pos_y
a.fin_z = cops_odom[0]["sub"].cur_alt

ball_vx = 0.0
ball_vy = 0.0

rstick = 0.0
lstick = 0.0

center_x = 0.0
center_y = 0.0

while True:
    print " "
    print " "
    print "WELCOME TO PONG!!"
    print " "
    print "center your squad-of-quads and yaw hard left to start!"

    while True:
        io = 0

        if abs(a.stick_map[3]) > 0.5: break
        if b.click == "A": break

        for cop in cops_odom:
            if abs(a.stick_map[0]) < 0.01 and abs(a.stick_map[1]) < 0.01 and abs(a.stick_map[2]) < 0.01:
                a.fin_x = cops_odom[0]["sub"].cur_pos_x + offs_x[io]
                a.fin_y = cops_odom[0]["sub"].cur_pos_y + offs_y[io]
                a.fin_z = cops_odom[0]["sub"].cur_alt

            else:
                a.fin_x = cops_odom[0]["sub"].cur_pos_x + a.x_offset + offs_x[io]
                a.fin_y = cops_odom[0]["sub"].cur_pos_y + a.y_offset + offs_y[io]
                a.fin_z = cops_odom[0]["sub"].cur_alt + a.z_offset

            cc.publish_odom(cop["pub"], a.fin_x, a.fin_y, 15.0 + offs_alt[io], prefix = cops_odom[0]["prefix"])

            time.sleep(0.05)

            io = io + 1

    center_x = cops_odom[0]["sub"].cur_pos_x
    center_y = cops_odom[0]["sub"].cur_pos_y

    ball_vx = 0.0
    ball_vy = 0.0

    rstick = 0.0
    rstick = 0.0

    print " "
    print "great job! get ready..."
    print " "
    time.sleep(0.5)

    ball_dir = -1.0
    ball_vx = 0.5
    ball_vy = 0.7

    while True:
        if b.click == "RTL":
            break

        if rstick < 5.0 and a.stick_map[2] < 0.0:
            rstick = rstick - a.stick_map[2]*0.075
        if rstick > -5.0 and a.stick_map[2] > 0.0:
            rstick = rstick - a.stick_map[2]*0.075

        if lstick < 5.0 and a.stick_map[0] > 0.0:
            lstick = lstick + a.stick_map[0]*0.075
        if lstick > -5.0 and a.stick_map[0] < 0.0:
            lstick = lstick + a.stick_map[0]*0.075

        adj_offs_y[1] = offs_y[1] + lstick
        adj_offs_y[2] = offs_y[2] + lstick

        adj_offs_y[3] = offs_y[3] + rstick
        adj_offs_y[4] = offs_y[4] + rstick

        adj_offs_y[0] = offs_y[0]

        io = 0

        for cop in cops_odom:
            if True:
                a.fin_x = center_x + offs_x[io]
                a.fin_y = center_y + adj_offs_y[io]

                cc.publish_odom(cop["pub"], a.fin_x, a.fin_y, 15.0 + offs_alt[io], prefix = cops_odom[0]["prefix"])

            io = io + 1

            time.sleep(0.01)

        offs_x[0] = offs_x[0] + ball_vx*0.075*ball_dir
        offs_y[0] = offs_y[0] + ball_vy*0.075

        if abs(offs_y[0]) > 5.0:
            ball_vy = -ball_vy

        ls = (cops_odom[1]["sub"].cur_pos_y + cops_odom[2]["sub"].cur_pos_y)/2.0
        rs = (cops_odom[3]["sub"].cur_pos_y + cops_odom[4]["sub"].cur_pos_y)/2.0

        if cops_odom[0]["sub"].cur_pos_x - center_x > 5.0:
            if abs(cops_odom[0]["sub"].cur_pos_y - rs) < 2.5:
                ball_dir = -1.0
                print "SLAM!"

        if cops_odom[0]["sub"].cur_pos_x - center_x < -5.0:
            if abs(cops_odom[0]["sub"].cur_pos_y - ls) < 2.5:
                ball_dir = 1.0
                print "SLAM!"

        if abs(cops_odom[0]["sub"].cur_pos_x - center_x) > 7.0:
            print " "
            print " "
            print "DAAAAAMN YOU SUCK! TRY AGAIN!"
            offs_x[0] = 0.0
            offs_y[0] = 0.0

            b.click = ""

            time.sleep(2.0)
            break

    if b.click == "RTL":
        break

print "copter landing!"

sr = cc.smart_rtl()

print "so long!"

time.sleep(1.0)


