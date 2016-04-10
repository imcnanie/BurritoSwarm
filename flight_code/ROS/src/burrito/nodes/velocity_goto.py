#!/usr/bin/env python  
import roslib

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
        self.throttle_update = 0.0
        self.attitude_publish = True


        self.pid_throttle = pid_controller.PID(P = 0.8, I = 0.8, D = 0.8, Integrator_max=1, Integrator_min=0)
        self.pid_throttle.setPoint(10)


       
        

        self.setHome = False
        self.home_lat = 0.0
        self.home_lon = 0.0
        self.home_alt = 0.0
        self.publish = True
        self.velocity_init()

        #self.velocity_init()



    def setmode(self,base_mode=0,custom_mode="OFFBOARD",delay=2):
        # Optimize time delay
        set_mode = rospy.ServiceProxy('/mavros/set_mode', mavros_msgs.srv.SetMode)  
        ret = set_mode(base_mode=base_mode, custom_mode=custom_mode)
        print "Changing modes: ", ret
        time.sleep(delay)



        
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
            #msg.pose.position.x = self.x
            #msg.pose.position.y = self.y
            #msg.pose.position.z = self.z
            msg.pose.position.x = 0.0
            msg.pose.position.y = 0.0
            msg.pose.position.z = 0.0
            
            
            # For demo purposes we will lock yaw/heading to north.
            yaw_degrees = self.yaw  # North
            yaw = radians(yaw_degrees)
            quaternion = quaternion_from_euler(0, 0, yaw)
            msg.pose.orientation = SP.Quaternion(*quaternion)
            if self.publish == True:
                self.pub.publish(msg)
                print "publishing position"
            rate.sleep()

    def publish_angular_linear_orientation(self):

        #att_pub = SP.get_pub_attitude_pose(queue_size=10)
        #thd_pub = SP.get_pub_attitude_throttle(queue_size=10)
        vel_pub = SP.get_pub_velocity_cmd_vel(queue_size=10)
        
        rate = rospy.Rate(10)   # 10hz
        
        ## msg = SP.PoseStamped(
        ##     header=SP.Header(
        ##         frame_id="base_footprint",  # no matter, plugin don't use TF
        ##         stamp=rospy.Time.now()),    # stamp should update
        ## )
        
        while not rospy.is_shutdown():
            #msg.pose.position.x = self.x
            #msg.pose.position.y = self.y
            #msg.pose.position.z = self.z
            twist = SP.TwistStamped(header=SP.Header(stamp=rospy.get_rostime()))
            twist.twist.linear = SP.Vector3(x=0, y=0, z=0)
            twist.twist.angular = SP.Vector3(z=-0.4)
            print "publishing orientation"
            vel_pub.publish(twist)

    def publish_orientation(self, ang=180):

        
        
        att_pub = SP.get_pub_attitude_pose(queue_size=10)
        
        #thd_pub = SP.get_pub_attitude_throttle(queue_size=10)
        #vel_pub = SP.get_pub_velocity_cmd_vel(queue_size=10)
        
        rate = rospy.Rate(10)   # 10hz
        
        ## msg = SP.PoseStamped(
        ##     header=SP.Header(
        ##         frame_id="base_footprint",  # no matter, plugin don't use TF
        ##         stamp=rospy.Time.now()),    # stamp should update
        ## )
        
        while not rospy.is_shutdown():
            #msg.pose.position.x = self.x
            #msg.pose.position.y = self.y
            #msg.pose.position.z = self.z


            pose = SP.PoseStamped(header=SP.Header(stamp=rospy.get_rostime()))
            q = quaternion_from_euler(0, 0, ang)
            pose.pose.orientation = SP.Quaternion(*q)
            
            #thd_pub.publish(data=self.throttle_update)
            #thd_pub.publish(data=0.6)
            
            att_pub.publish(pose)
            
            print "pose orientation: ", self.throttle_update
            
            
    def publish_pose_thread(self):
        #t = Thread(target=self.publish_orientation, args=())
        t = Thread(target=self.publish_pose, args=())
        t.daemon = True
        t.start()

        
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

        self.pid_alt = pid_controller.PID()
        self.pid_alt.setPoint(1.0)
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



        #att_pub = SP.get_pub_attitude_pose(queue_size=10)
        #thd_pub = SP.get_pub_attitude_throttle(queue_size=10)
            
            
            #thd_pub.publish(data=self.throttle_update)
            #thd_pub.publish(data=0.6)
            
            
            


        
        rate = rospy.Rate(10)   # 10hz
        magnitude = 1  # in meters/sec

        msg = SP.TwistStamped(
            header=SP.Header(
                frame_id="base_footprint",  # no matter, plugin don't use TF
                stamp=rospy.Time.now()),    # stamp should update
        )
        i =0
        while not rospy.is_shutdown():
            #print "publishing velocity"
            self.throttle_update = self.pid_throttle.update(self.current_alt)
            pid_offset = self.pid_alt.update(self.current_alt)
            if self.use_pid:
                msg.twist.linear = geometry_msgs.msg.Vector3(self.vx*magnitude, self.vy*magnitude, self.vz*magnitude+pid_offset)
            else:
                msg.twist.linear = geometry_msgs.msg.Vector3(self.vx*magnitude, self.vy*magnitude, self.vz*magnitude)
            #print msg.twist.linear
            # For demo purposes we will lock yaw/heading to north.
            yaw_degrees = self.yaw  # North
            yaw = radians(yaw_degrees)
            quaternion = quaternion_from_euler(0, 0, yaw)
            if self.velocity_publish:
                #msg.twist.angular.z = 0.5
                self.pub_vel.publish(msg)
                #print "PID: ", pid_offset


            
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

        #print "Current Lat", self.current_lat, "Current Lon", self.current_lon
        
        if wait:
            rate = rospy.Rate(5)
            while not self.done and not rospy.is_shutdown():
                rate.sleep()
 
    def temp(self, topic):
        pass

    def velocity_gps_goto(self, lat, lon, alt):
        pid_lat = pid_controller.PID()
        
        self.pid_alt.setPoint(alt)
        self.use_pid = True
        pid_lat.setPoint(lat)

        self.set_publish(False)
        self.set_velocity_publish(True)
        
        while abs(self.current_lat - lat) > 0.2:
            vel_x = pid_lat.update(self.current_lat)
            if vel_x > 5:
                vel_x = 5
            if vel_x < -5:
                vel_x = -5
            #self.publish_orientation()
            self.yaw = 67
            self.set_velocity(vel_x, 0, 0)
            print "ABS current lat min lat: ", abs(self.current_lat - lat)
            #print "Current lat, target lat: ", self.current_lat, " ", lat

        self.set_publish(False)
            
    def land_velocity(self):
        self.use_pid = False
        #self.set_velocity(0, 0, -0.4)
        self.set_velocity(0, 0, -1)
        while self.current_alt > 0.2:
            pass #print "landing: ", self.current_alt
        print "Landed, disarming"
        self.set_velocity(0, 0, 0)
        #self.disarm()

    def takeoff_velocity(self, alt=7):
        # Make margin hella better
        
        #ret = command.takeoff(altitude=alt)
        #takeoff = rospy.ServiceProxy('/mavros/cmd/takeoff', mavros_msgs.srv.CommandTOL)
        #takeoff( 0, 0, lat, lon, 1)
        self.use_pid = False
        while abs(self.current_alt - alt) > 0.2:
            #self.set_local_coord(0, 0, alt, delay=0.1)
            self.x = 0
            self.y = 0
            self.z = 10
            self.set_velocity(0, 0, 2.5)
            #print "ye ",abs(self.current_alt - alt)
            #print "going to alt", self.current_alt,  alt

        time.sleep(2)
        
        rospy.loginfo("Reached target Alt!")
        self.use_pid = True

    def blocked_yaw(self, yaw = 167):
        att_pub = SP.get_pub_attitude_pose(queue_size=10)
        thd_pub = SP.get_pub_attitude_throttle(queue_size=10)

        #while not rospy.is_shutdown():
        pose = SP.PoseStamped(header=SP.Header(stamp=rospy.get_rostime()))
        q = quaternion_from_euler(0, 0, self.yaw)
        pose.pose.orientation = SP.Quaternion(*q)
        
        
        if self.attitude_publish or True:
            att_pub.publish(pose)
            thd_pub.publish(data=0.4)
            
            print "pose orientation: ", self.throttle_update
            #self.attitude_publish = False
        
if __name__ == '__main__':
    brekin = brekinIt()
    brekin.subscribe_pose_thread()
    
    time.sleep(1)

    brekin.set_velocity_publish(True)

    time.sleep(.1)

    
    print "set mode"
    brekin.setmode(custom_mode="OFFBOARD")
    brekin.arm()

    time.sleep(.1)
    brekin.takeoff_velocity()

    print "out of takeoff"


    brekin.set_publish(False)


    brekin.blocked_yaw()
    print "blocked_yaw"
    time.sleep(1)
    #brekin.set_velocity_publish(True)
    #print "setting velocity"
    #brekin.set_velocity(-1, 0, 0.2)
    print "going to gps"
    brekin.velocity_gps_goto(465700.071181, brekin.current_lon, 10)
    print "at gps, waiting"
    time.sleep(1)
    print "done"
    #brekin.set_velocity(0, 0, 0.2, yaw=180)
    #time.sleep(5)
    #brekin.set_local_coord(0, 0, 10, delay=10)
    brekin.land_velocity()
    brekin.set_velocity_publish(False)
    while not rospy.is_shutdown():
        #print "Current Lat: ", brekin.current_lat, " Current Lon: ", brekin.current_lon
        print "Landed!"
