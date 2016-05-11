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

rospy.init_node("copter_broadcast_cursor")
br = tf.TransformBroadcaster() #test

print "initializing copter..."

cop = velocity_goto.posVel(copter_id = "1")

cop.start_subs()
time.sleep(1.0)

cop.subscribe_pose_thread()
time.sleep(0.1)

cop.start_navigating()
time.sleep(0.1)

#cop.setmode(custom_mode = "MANUAL")
cop.arm()
time.sleep(0.5)

cop.setmode(custom_mode = "OFFBOARD")

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

    q = cop.pose_open

    # cursor
    br.sendTransform((cop.cur_pos_x - a.fin_x, cop.cur_pos_y - a.fin_y, 0.0),
                     (q.x, q.y, q.z, q.w),
                     rospy.Time.now(),
                     "cursor",
                     "fcu")

    time.sleep(0.1)

    #try:
    #    print sqrt((cop.final_pos_x - cop.cur_pos_x) * 2.0 + (cop.final_pos_y - cop.cur_pos_y) * 2.0)
    #except:
    #    print "breaks"

    cop.update(a.fin_x, a.fin_y, a.fin_z)

    if abs(a.stick_map[0]) < 0.01 and abs(a.stick_map[1]) < 0.01 and abs(a.stick_map[2]) < 0.01:
        a.fin_x = cop.cur_pos_x
        a.fin_y = cop.cur_pos_y
        a.fin_z = cop.cur_alt
    else:
        a.fin_x = cop.cur_pos_x + a.x_offset
        a.fin_y = cop.cur_pos_y + a.y_offset
        a.fin_z = cop.cur_alt + a.z_offset
 

    #time.sleep(0.025)

