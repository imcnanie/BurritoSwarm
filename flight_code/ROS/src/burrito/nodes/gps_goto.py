#!/usr/bin/env python  
import roslib
#roslib.load_manifest('learning_tf')

import rospy
import tf
from math import *
from nav_msgs.msg import Odometry
import geometry_msgs.msg
import mavros
import mavros_msgs.srv
from mavros import setpoint as SP
from mavros import command
from threading import Thread
from tf.transformations import quaternion_from_euler
import time
import threading
import thread
import pid_controller
print "broadcasting"

#roslib.load_manifest('odom_publisher')

#import mavros
#mavros.set_namespace()
#pub = SP.get_pub_position_local(queue_size=10)
class brekinIt:
    def __init__(self):
        rospy.init_node('gps_goto')
        mavros.set_namespace()  # initialize mavros module with default namespace
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.current_lat = 0.0
        self.current_lon = 0.0
        self.current_alt = 0.0

        self.setHome = False
        self.home_lat = 0.0
        self.home_lon = 0.0
        self.home_alt = 0.0
        self.publish = True
        self.velocity_init()

        #self.velocity_init()
        
    def handle_pose(self, msg):
        pos = msg.pose.pose.position
        #q = msg.pose.pose.orientation
        #msg.pose.pose.position.x = 465720.756519
        #pub.publish(msg)
    
        self.current_lat = pos.x 
        self.current_lon = pos.y
        self.current_alt = pos.z


        if not self.setHome:
            self.home_lat = self.current_lat
            self.home_lon = self.current_lon
            self.home_alt = self.current_alt
            self.setHome = True
        
        #print "X ",q.x, " Y ", q.y, " Z ", q.z, " W ", q.w
    
        #br = tf.TransformBroadcaster()
        #br.sendTransform(( pos.x - 465710.758519, pos.y - 5249465.35307,  pos.z),
        #                 (q.x, q.y, q.z, q.w),
        #                 rospy.Time.now(),
        #                 "f1",
        #                 "fcu")

    def reset_home(self):
        self.setHome = False
        
    def subscribe_pose(self):
        #rate = rospy.Rate(10.0)
        #while not rospy.is_shutdown():
        rospy.Subscriber('/mavros/global_position/local',
                         Odometry,
                         self.handle_pose)
         
        rospy.spin()

    def subscribe_pose_thread(self):
        s = Thread(target=self.subscribe_pose, args=())
        s.daemon = True
        s.start()

    def gps_goto(self, lat, lon, alt, delay=0):
        #print "in coord"
        self.x = lat - self.home_lat
        self.y = lon - self.home_lon
        self.z = alt
        time.sleep(delay)
        
    def set_coord(self, lat, lon, alt, delay=0):
        #print "in coord"
        self.x = lat - self.home_lat
        self.y = lon - self.home_lon
        self.z = alt
        time.sleep(delay)

    def set_local_coord(self, lat, lon, alt, delay=0):
        #print "in coord"
        self.x = lat
        self.y = lon
        self.z = alt
        time.sleep(delay)


    def set_publish(self, pub):
        self.publish = pub
        
    def publish_pose(self):
        self.pub = SP.get_pub_position_local(queue_size=10)
        rate = rospy.Rate(10)   # 10hz
        
        msg = SP.PoseStamped(
            header=SP.Header(
                frame_id="base_footprint",  # no matter, plugin don't use TF
                stamp=rospy.Time.now()),    # stamp should update
        )
        
        while not rospy.is_shutdown():
            msg.pose.position.x = self.x
            msg.pose.position.y = self.y
            msg.pose.position.z = self.z

            
            
            # For demo purposes we will lock yaw/heading to north.
            yaw_degrees = 0  # North
            yaw = radians(yaw_degrees)
            quaternion = quaternion_from_euler(0, 0, yaw)
            msg.pose.orientation = SP.Quaternion(*quaternion)
            if self.publish == True:
                self.pub.publish(msg)
                print "publishing position"
            rate.sleep()

    def publish_pose_thread(self):
        t = Thread(target=self.publish_pose, args=())
        t.daemon = True
        t.start()

        
    def takeoff(self, alt=4):
        # Make margin hella better

        lat = self.current_lat
        lon = self.current_lon

        #ret = command.takeoff(altitude=alt)
        #takeoff = rospy.ServiceProxy('/mavros/cmd/takeoff', mavros_msgs.srv.CommandTOL)
        #takeoff( 0, 0, lat, lon, 1)  
        while abs(self.current_alt - alt) > 0.5:
            #self.set_local_coord(0, 0, alt, delay=0.1)
            self.x = 0
            self.y = 0
            self.z = 10
            print "going to alt", self.current_alt,  alt


        time.sleep(2)
        
        rospy.loginfo("Reached target Alt!")

    def arm(self):
        print dir(mavros)
        arm = rospy.ServiceProxy('/mavros/cmd/arming', mavros_msgs.srv.CommandBool)  
        print "Arm: ", arm(True)
        
    def disarm(self):
        arm = rospy.ServiceProxy('/mavros/cmd/arming', mavros_msgs.srv.CommandBool)  
        print "Disarm: ", arm(False)

    def land(self):
        # Make margin hella better

        lat = self.current_lat
        lon = self.current_lon

        #ret = command.takeoff(altitude=alt)
        land = rospy.ServiceProxy('/mavros/cmd/land', mavros_msgs.srv.CommandTOL)
        land(0, 0, lat, lon, 0)  
        #while abs(self.current_alt - alt) > 0.5:
        #    self.set_coord(lat, lon, alt, delay=0.1)
        #    print "going to alt", self.current_alt - alt


        time.sleep(2)
        
        rospy.loginfo("Reached target Alt!")
        
    ##def land(self):
    ##    # Simulate a slow landing.
    ##    lat = self.current_lat
    ##    lon = self.current_lon
    ##    
    ##    self.set_coord(lat, lon,  8.0, delay=5)
    ##    self.set_coord(lat, lon,  3.0, delay=5)
    ##    self.set_coord(lat, lon,  2.0, delay=2)
    ##    self.set_coord(lat, lon,  1.0, delay=2)
    ##    self.set_coord(lat, lon,  0.0, delay=2)
    ##    self.set_coord(lat, lon, -0.2, delay=2)

    ##    rospy.loginfo("Landed?")
        
    def setmode(self,base_mode=0,custom_mode="OFFBOARD",delay=2):
        # Optomize time delay
        # Optimize spelling of Optimize

        set_mode = rospy.ServiceProxy('/mavros/set_mode', mavros_msgs.srv.SetMode)  
        ret = set_mode(base_mode=base_mode, custom_mode=custom_mode)
        print "Changing modes: ", ret
        time.sleep(delay)



    
    """
    This /class/ sends position targets to FCU's position controller
    """
    def velocity_init(self):
        self.vx = 0.0
        self.vy = 0.0
        self.vz = 0.0
        self.yaw = 0.0
        self.velocity_publish = False
        self.use_pid = True

        self.pid_c = pid_controller.PID()
        self.pid_c.setPoint(4.0)
        # publisher for mavros/setpoint_position/local
        self.pub_vel = SP.get_pub_velocity_cmd_vel(queue_size=10)
        # subscriber for mavros/local_position/local
        self.sub = rospy.Subscriber(mavros.get_topic('local_position', 'local'), SP.PoseStamped, self.temp)
 
        try:
            thread.start_new_thread(self.navigate, ())
        except:
            fault("Error: Unable to start thread")
 
        # TODO(simon): Clean this up.
        self.done = False
        self.done_evt = threading.Event()
 
    def navigate(self):
        rate = rospy.Rate(10)   # 10hz
        magnitude = 1  # in meters/sec

        msg = SP.TwistStamped(
            header=SP.Header(
                frame_id="base_footprint",  # no matter, plugin don't use TF
                stamp=rospy.Time.now()),    # stamp should update
        )
        i =0
        while not rospy.is_shutdown():
            pid_offset = self.pid_c.update(self.current_alt)
            if self.use_pid:
                msg.twist.linear = geometry_msgs.msg.Vector3(self.vx*magnitude, self.vy*magnitude, self.vz*magnitude+pid_offset)
            else:
                msg.twist.linear = geometry_msgs.msg.Vector3(self.vx*magnitude, self.vy*magnitude, self.vz*magnitude)
            print msg.twist.linear
            # For demo purposes we will lock yaw/heading to north.
            yaw_degrees = self.yaw  # North
            yaw = radians(yaw_degrees)
            quaternion = quaternion_from_euler(0, 0, yaw)
            if self.velocity_publish == True:
                
                self.pub_vel.publish(msg)
                print "PID: ", pid_offset
            rate.sleep()
            i +=1

    def set_velocity_publish(self,pub):
        self.velocity_publish = pub
            
    def set_velocity(self, vx, vy, vz, yaw=0.0, delay=0, wait=False):
        self.done = False
        self.vx = vx
        self.vy = vy
        self.vz = vz
        
        self.yaw = yaw

        print "Current Lat", self.current_lat, "Current Lon", self.current_lon
        
        if wait:
            rate = rospy.Rate(5)
            while not self.done and not rospy.is_shutdown():
                rate.sleep()
 
    def temp(self, topic):
        pass

    def land_velocity(self):
        self.use_pid = False
        self.set_velocity(0, 0, -0.4)
        while self.current_alt > 0:
            print "landing: ", self.current_alt
        print "Landed, disarming"
        brekin.set_velocity(0, 0, 0)
        #self.disarm()
        
                
if __name__ == '__main__':
    brekin = brekinIt()
    brekin.subscribe_pose_thread()
    
    time.sleep(1)
    #brekin.setmode(custom_mode="MANUAL")
    
    brekin.publish_pose_thread()
    time.sleep(2)
    print "set mode"
    brekin.setmode()
    brekin.arm()
    time.sleep(.1)
    brekin.takeoff()
    #brekin.setmode()
    #brekin
    #brekin.set_velocity(0,0,0.1)
    print "out of takeoff"
    #time.sleep(10)

    brekin.set_publish(False)


    time.sleep(1)
    brekin.set_velocity_publish(True)
    print "setting velocity"
    brekin.set_velocity(1, 0, 0.2)
    
    time.sleep(5)
    brekin.set_velocity(0, 0, 0.2, yaw=180)
    time.sleep(5)
    #brekin.set_local_coord(0, 0, 10, delay=10)
    brekin.land_velocity()
    brekin.set_velocity_publish(False)
    while not rospy.is_shutdown():
        print "Current Lat: ", brekin.current_lat, " Current Lon: ", brekin.current_lon



    
