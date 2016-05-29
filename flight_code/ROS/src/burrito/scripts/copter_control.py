#!/usr/bin/env python  
import roslib
import rospy
import tf
import std_msgs
from math import *
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Point, Quaternion
from sensor_msgs.msg import NavSatFix
from std_msgs.msg import Bool
import geometry_msgs.msg
import mavros
import mavros_msgs.srv
from mavros import setpoint as SP
from mavros import command
from threading import Thread
from tf.transformations import quaternion_from_euler
from tf.transformations import euler_from_quaternion
import time
import threading
import thread
import pid_controller
from random import randint
import rosgraph.masterapi
import utm
import PyKDL as kdl
import numpy as np
import count_copters

# Covariance
P = np.mat(np.diag([0.0]*3))

IS_APM = False # Need to eventually detect

class CopterControl:
    def __init__(self):
        self.num_cops = count_copters.count_copters()

    def smart_rtl(self):        
        self.initial_alt_drop = 5

        self.cops = ["/copter"+str(x+1)+"/" for x in range(self.num_cops)]
        self.cops_odom = []

        for prefix in self.cops:
            pub = rospy.Publisher(prefix+'hellacopters/setpoint_odom/cmd_odom', Odometry, queue_size=10)
            sub = self.Subscribers()
            rospy.Subscriber(prefix+'mavros/global_position/local',
                             Odometry,
                             sub.handle_pose)
            rospy.Subscriber(prefix+'hellacopters/',
                             Odometry,
                             sub.handle_home)
            rospy.Subscriber(prefix+'hellacopters/setpoint_odom/reached',
                             Bool,
                             sub.handle_reached)
            rospy.Subscriber(prefix+'')
            self.cops_odom.append({"prefix":prefix, "pub":pub, "sub":sub, "hsub":hsub})

        self.sorted_copters = []
        copters_by_alt = {}

        time.sleep(0.25)

        for cop in cops_odom:
            copters_by_alt[cop] = cop['sub'].cur_alt

        self.sorted_copters = sorted(copters_by_alt)

        for w in self.sorted_copters[::-1][:-1]:
            #self.raise_cops(w)

            raise_height = w['sub'].cur_alt + 5.0

            self.publish_odom(w['sub'].cur_pos_x, w['sub'].cur_pos_y, raise_height)
            while cur_alt < raise_height-1.0:
                time.sleep(0.1)
            
        for x in self.sorted_copters:
            #self.land_cop(x)

            drop_height = w['sub'].cur_pos_x - self.initial_alt_drop

            print "Copter dropping..."

            self.publish_odom(w['sub'].cur_pos_x, w['sub'].cur_pos_y, drop_height)
            while w['sub'].cur_alt > drop_height+2.0:
                time.sleep(0.01)
        
            print "Going to home location..."
            time.sleep(0.25)

            self.publish_odom(w['hsub'].home_lat, w['hsub'].home_lon, w['hsub'].home_alt)
            while not cop.reached:
                cur_pos_x, cur_pos_y, cur_alt = cop.get_lat_lon_alt()
                time.sleep(0.025)

            print "land!"

            self.setmode(custom_mode="AUTO.LAND")


    def safe_takeoff(self, initial_coords, alt = 20.0):
        #offsets = [(0,0),(2,0)], etc.

        self.alt = alt
        
        self.cops = ["/copter"+str(x+1)+"/" for x in range(self.num_cops)]
        self.cops_odom = []

        for prefix in self.cops:
            pub = rospy.Publisher(prefix+'hellacopters/setpoint_odom/cmd_odom', Odometry, queue_size=10)
            sub = self.Subscribers()
            rospy.Subscriber(prefix+'mavros/global_position/local',
                             Odometry,
                             sub.handle_pose)
            rospy.Subscriber(prefix+'hellacopters/setpoint_odom/reached',
                             Bool,
                             sub.handle_reached)
            self.cops_odom.append({"prefix":prefix,"pub":pub,"sub":sub})

        self.center_x = self.cops_odom[0]['sub'].cur_pos_x
        self.center_y = self.cops_odom[0]['sub'].cur_pos_y

        for i in self.cops_odom[::-1]:
            print "Taking off cop: ", i
            self.takeoff_cop(i)
            
    def takeoff_cop(self, args):
        self.setmode(prefix=args['prefix'], custom_mode="OFFBOARD")
        self.arm(prefix=args['prefix'])
        #self.cops[id].setmode(custom_mode = "OFFBOARD")
        #self.cops[id].arm()

        time.sleep(0.25)

        self.takeoff_velocity(args['pub'], args['sub'], prefix=args['prefix'])

        print "OUT OF TAKEOFF VELOCITY"
        #self.cops[id].takeoff_velocity(alt = self.alt)
        #self.cops[id].update(self.center_x + self.offs_x[id], self.center_y + self.offs_y[id], self.alt)

        hz = rospy.Rate(10)
        while not args['sub'].reached:
            print "GOING TO POSITION"
            lat = self.center_x + offs_x[self.cops_odom.index(args)]
            lon = self.center_y + offs_y[self.cops_odom.index(args)]
            self.publish_odom(args['pub'], lat, lon, self.alt, prefix=args['prefix'])
            hz.sleep()

    def publish_odom(self, odom_pub, lat, lon, alt, yaw=180, prefix="/copter1/", publish_odom_tf=True):
        print "publishing mf odom"
        msg = Odometry()
        msg.header.stamp = rospy.Time.now()
        msg.header.frame_id = prefix # i.e. '/odom'
        msg.child_frame_id = 'hellacopters' # i.e. '/base_footprint'
        
        msg.pose.pose.position = Point(lat, lon, alt)

        msg.pose.pose.position.x = lat
        msg.pose.pose.position.x = lon
        msg.pose.pose.position.x = alt

        pos = (msg.pose.pose.position.x,
               msg.pose.pose.position.y,
               msg.pose.pose.position.z)
        
        #ori = (msg.pose.pose.orientation.x,
        #       msg.pose.pose.orientation.y,
        #       msg.pose.pose.orientation.z,
        #       msg.pose.pose.orientation.w)

        ori = (0.0, 0.0, 0.0, 0.0)    

        # Publish odometry message
        odom_pub.publish(msg)
        
        # Also publish tf if necessary
        if publish_odom_tf:
            tf_br = tf.TransformBroadcaster()
            tf_br.sendTransform(pos, ori, msg.header.stamp, msg.child_frame_id, msg.header.frame_id)
        
    def takeoff_velocity(self, pub, sub, prefix="/copter1/", alt=7):
        self.alt_control = False

        while sub.cur_alt < abs(alt - 1.0):
            print "CUR ALT: ", sub.cur_alt, "GOAL: ", alt
            lat = sub.cur_pos_x
            lon = sub.cur_pos_y
            self.publish_odom(pub, lat, lon, self.alt, prefix=prefix)
            #self.set_velocity(0, 0, 1.5)
            #self.update(self.cur_pos_x, self.cur_pos_y, alt)

        time.sleep(0.1)
        #self.set_velocity(0, 0, 0)

        self.final_alt = alt

        print "THE FINAL ALT: ", alt
        
        rospy.loginfo("Reached target Alt!")
            
    def arm(self, prefix="/copter1/"):
        arm = rospy.ServiceProxy(prefix+'mavros/cmd/arming', mavros_msgs.srv.CommandBool)  
        print "Arm: ", arm(True)
        
    def disarm(self, prefix="/copter1/"):
        arm = rospy.ServiceProxy(prefix+'mavros/cmd/arming', mavros_msgs.srv.CommandBool)  
        print "Disarm: ", arm(False)
            
    def setmode(self, prefix="/copter1/",base_mode=0,custom_mode="OFFBOARD",delay=0.1):
        set_mode = rospy.ServiceProxy(prefix+'mavros/set_mode', mavros_msgs.srv.SetMode)  
        if IS_APM:
            if custom_mode == "OFFBOARD":
                custom_mode = "GUIDED"
            if custom_mode == "AUTO.LAND":
                custom_mode = "LAND"
            if custom_mode == "MANUAL":
                custom_mode = "STABILIZE"
            if custom_mode == "POSCTL":
                custom_mode = "LOITER"
        ret = set_mode(base_mode=base_mode, custom_mode=custom_mode)
        print "Changing modes: ", ret
        time.sleep(delay)

            
    class Subscribers:
        def __init__(self, is_home = False):
            self.cur_pos_x = 0.0
            self.cur_pos_y = 0.0
            self.cur_alt = 0.0

            self.home_x = 0.0
            self.home_y = 0.0
            self.home_z = 0.0

            self.reached = False

        def handle_pose(self, msg):
            pos = msg.pose.pose.position
            qq = msg.pose.pose.orientation
            
            self.pose_open = qq
            
            q = (msg.pose.pose.orientation.x,
                 msg.pose.pose.orientation.y,
                 msg.pose.pose.orientation.z,
                 msg.pose.pose.orientation.w)
            
            euler = euler_from_quaternion(q)
            
            self.cur_rad = euler[2]

            self.cur_pos_x = pos.x 
            self.cur_pos_y = pos.y
            self.cur_alt = pos.z

        def handle_home(self, msg):
            pos = msg.pose.pose.position
            
            self.home_x = pos.x
            self.home_y = pos.y
            self.home_z = pos.z

        def handle_reached(self, msg):
            self.reached = msg.data

            
if __name__ == "__main__":
    rospy.init_node("safe_takeoff")

    print "testing takeoff"

    offs_x = [0.0, -6.5, -6.5, 6.5, 6.5]
    offs_y = [0.0, 2.5, -2.5, 2.5, -2.5]
    initial_coords = []
    for x in range(len(offs_x)):
        initial_coords.append((offs_x[x],offs_y[x]))

    cc = CopterControl()

    print "Taking of ", cc.num_cops , " copters."
    
    st = cc.safe_takeoff(initial_coords)

    time.sleep(1.0)

    print "Takeoff success, landing"    

    st = 
