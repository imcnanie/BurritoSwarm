import roslib
import rospy
import std_msgs

from threading import Thread

import math
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


print "initializing copters..."

rospy.init_node("talker")

offs_x = [0.0, 2.0, 4.0, 6.0, 8.0]
offs_y = [0.0, 1.0, 2.0, 3.0, 4.0]
offs_z = [0.0, 0.0, 0.0, 0.0, 0.0]

cops = []

for i in range(5):
    cops.append(velocity_goto.posVel(copter_id = str(i+1)))

    cops[i].start_subs()
    time.sleep(0.1)

    cops[i].subscribe_pose_thread()
    time.sleep(0.1)

    cops[i].start_navigating()
    time.sleep(0.1)

history_x = [0.0] * 25
history_y = [0.0] * 25
history_z = [0.0] * 25

velocity_goto.SafeTakeoff(cops, offs_x, offs_y, alt = 15.0)

for i in range(5):
    history_x.append(cops[0].cur_pos_x + offs_x[4-i])
    history_y.append(cops[0].cur_pos_y + offs_y[4-i])
    history_z.append(cops[0].cur_alt + offs_z[4-i])

print "ready"

art = artoo()
art.start_subbing()

hlen = len(history_x)-1
thresh = 3.0

chill = [True] * 4

while True:
    cops[0].set_velocity(art.x_offset, art.y_offset, art.z_offset)

    a = (history_x[hlen]-cops[0].cur_pos_x)
    b = (history_y[hlen]-cops[0].cur_pos_y)
    c = (history_z[hlen]-cops[0].cur_alt)

    if math.sqrt(a**2 + b**2 + c**2) > thresh:
        history_x.pop(0)
        history_y.pop(0)
        history_z.pop(0)

        history_x.append(cops[0].cur_pos_x)
        history_y.append(cops[0].cur_pos_y)
        history_z.append(cops[0].cur_alt)

        chill[0] = False

    for i in range(len(chill)):
        if not chill[i]:
            cops[i+1].update(history_x[hlen-(i+1)], history_y[hlen-(i+1)], history_z[hlen-(i+1)])

            a = (cops[i].cur_pos_x-cops[i+1].cur_pos_x)
            b = (cops[i].cur_pos_y-cops[i+1].cur_pos_y)
            c = (cops[i].cur_alt-cops[i+1].cur_alt)

            if math.sqrt(a**2 + b**2 + c**2) > 0.25:
                chill[i] = True

            if i == 1:
                print math.sqrt(a**2 + b**2 + c**2)

            if math.sqrt(a**2 + b**2 + c**2) > 5.0:
                try:
                    chill[i+1] = False
                except:
                    pass

    #time.sleep(0.025)

