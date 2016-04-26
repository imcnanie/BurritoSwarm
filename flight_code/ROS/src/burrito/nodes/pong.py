from nav_msgs.msg import Odometry
import std_msgs
import rosnode
import roslib
import rospy
import tf

from threading import Thread
from math import *
import random
import time
import ast
import os

import velocity_goto

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

cops = []

for i in range(5):
    cops.append(velocity_goto.posVel(copter_id = str(i+1)))

for cop in cops:
    cop.start_subs()
    time.sleep(1.0)

    cop.subscribe_pose_thread()
    time.sleep(0.1)

    cop.start_navigating()
    time.sleep(0.1)

i = 1

for cop in cops:
    #print i
    cop.setmode(custom_mode = "OFFBOARD")
    cop.arm()
    time.sleep(0.1)

    cop.takeoff_velocity()

    i = i +1

print "ready"

b = buttons()
b.start_subbing()

a = artoo()
a.start_subbing()

a.fin_x = cops[0].cur_pos_x
a.fin_y = cops[0].cur_pos_y
a.fin_z = cops[0].cur_alt

offs_x = [0.0, -6.0, -6.0, 6.0, 6.0]
offs_y = [0.0, 0.8, -0.8, 0.8, -0.8]

adj_offs_y = [0.0, 0.0, 0.0, 0.0, 0.0]

ball_vx = 0.0
ball_vy = 0.0

rstick = 0.0
lstick = 0.0

center_x = 0.0
center_y = 0.0

while True:
    print " "
    print "WELCOME TO PONG!!"
    print " "
    print "center your squad-of-quads and press A to start!"

    while True:
        io = 0

        #print b.click

        if b.click == "A": break

        for cop in cops:
            if abs(a.stick_map[0]) < 0.01 and abs(a.stick_map[1]) < 0.01 and abs(a.stick_map[2]) < 0.01:
                a.fin_x = cops[0].cur_pos_x + offs_x[io] 
                a.fin_y = cops[0].cur_pos_y + offs_y[io]
                a.fin_z = cops[0].cur_alt

            else:
                a.fin_x = cops[0].cur_pos_x + a.x_offset + offs_x[io]
                a.fin_y = cops[0].cur_pos_y + a.y_offset + offs_y[io]
                a.fin_z = cops[0].cur_alt + a.z_offset

            cop.update(a.fin_x, a.fin_y, 1.0)
  
            time.sleep(0.05)

            io = io + 1 

    center_x = cops[0].cur_pos_x
    center_y = cops[0].cur_pos_y

    print " "
    print "great job! get ready..."
    print " "
    time.sleep(0.5)

    ball_vx = 0.5
    ball_vy = 0.7

    while True:
        io = 0

        if b.click == "Pause":
            print "game paused..."
            while True:
                if b.click == "Pause":
                    print "game unpaused!"
                    break
                time.sleep(0.05)

        if rstick < 5.0 and a.stick_map[2] < 0.0:
            rstick = rstick - a.stick_map[2]*0.3 
        if rstick > -5.0 and a.stick_map[2] > 0.0:
            rstick = rstick - a.stick_map[2]*0.3

        if lstick < 5.0 and a.stick_map[0] > 0.0:
            lstick = lstick + a.stick_map[0]*0.3
        if lstick > -5.0 and a.stick_map[0] < 0.0:
            lstick = lstick + a.stick_map[0]*0.3 

        adj_offs_y[1] = offs_y[1] + rstick
        adj_offs_y[2] = offs_y[2] + rstick

        adj_offs_y[3] = offs_y[3] + lstick
        adj_offs_y[4] = offs_y[4] + lstick

        adj_offs_y[0] = offs_y[0]

        for cop in cops:
            if True:
                a.fin_x = center_x + offs_x[io]
                a.fin_y = center_y + adj_offs_y[io]

                cop.update(a.fin_x, a.fin_y, 1.0)
                
            time.sleep(0.01)

            io = io + 1

        offs_x[0] = offs_x[0] + ball_vx*0.05
        offs_y[0] = offs_y[0] + ball_vy*0.05

        if abs(offs_y[0]) > 4.3: # ball motion handling
            ball_vy = -ball_vy

        if offs_x[0] > 5.5:
            print "DANGER"
            if abs(offs_y[0] - rstick) < 0.8:
                ball_vx = -ball_vx
        if offs_x[0] < -5.5:
            print "DANGER"
            if abs(offs_y[0] - lstick) < 0.8:
                ball_vx = -ball_vx

        if abs(offs_x[0]) > 6.0:
            print " "
            print " "
            print "DAAAAAMN YOU SUCK! TRY AGAIN!"
            offs_x[0] = 0.0
            offs_y[0] = 0.0

            b.click = ""

            time.sleep(2.0)
            break
