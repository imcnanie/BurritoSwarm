#!/usr/bin/env python
"""Receives main wind messages and tells mavros to move
in that respective direction"""
import rospy

import sys,tty,termios
import mavros
import time
import threading
import thread


from math import *
from mavros.utils import *
from mavros import setpoint as SP
from tf.transformations import quaternion_from_euler

import geometry_msgs.msg
import std_msgs.msg


class _Getch:       
    def __call__(self):
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                ch = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return ch


class SetpointPosition:
    """
    This class sends position targets to FCU's position controller
    """
    def __init__(self):
        self.vx = 0.0
        self.vy = 0.0
        self.vz = 0.0
 
        # publisher for mavros/setpoint_position/local
        self.pub = SP.get_pub_velocity_cmd_vel(queue_size=10)
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
        while i<120:
            msg.twist.linear = geometry_msgs.msg.Vector3(self.vx*magnitude, self.vy*magnitude, self.vz*magnitude)  

            print msg.twist.linear
            # For demo purposes we will lock yaw/heading to north.
            yaw_degrees = 0  # North
            yaw = radians(yaw_degrees)
            quaternion = quaternion_from_euler(0, 0, yaw)
             
            self.pub.publish(msg)
            rate.sleep()
            i +=1

    def set(self, vx, vy, vz, delay=0, wait=True):
        self.done = False
        self.vx = vx
        self.vy = vy
        self.vz = vz
 
        if wait:
            rate = rospy.Rate(5)
            while not self.done and not rospy.is_shutdown():
                rate.sleep()
 
    def temp(self, topic):
        pass



def input_key(roll,pitch,yaw,thrust): #these are just inputs. not related to orienation.
    k = None
    inkey = _Getch()
    k = inkey()
    print "================="
    if k == "q":
       print "quit"
       return False, roll, pitch, yaw, thrust
    if k == "a":
        yaw -= 0.01
    elif k == "d":
        yaw += 0.01
    elif k == "s":
        thrust -= 0.01
    elif k == "w":
        thrust += 0.01
    elif k == "D":
        roll -= 0.01
    elif k == "C":
        roll += 0.01
    elif k == "B":
        pitch -= 0.01
    elif k == "A":
        pitch += 0.01
    elif k == "z":
        roll = 0
        pitch = 0
        yaw = 0
        thrust = 0
    else:
        print "nothing"
    print "roll: " + str(roll) 
    print "pitch: " + str(pitch) 
    print "yaw: " + str(yaw) 
    print "thrust: " + str(thrust) 
    return True, roll, pitch, yaw, thrust

def main():
    yaw = 0.0
    thrust = 0.0
    roll = 0.0
    pitch = 0.0
    flag = True
    rospy.init_node('setpoint_position_demo')
    mavros.set_namespace()  # initialize mavros module with default namespace
    rate = rospy.Rate(10)
    setpoint = SetpointPosition()
    i = 0
    while flag:
        #flag, roll, pitch, yaw, thrust = input_key(roll, pitch, yaw, thrust)
        print roll
        print "here"
        roll = sin(i) 
        setpoint.set(10, pitch, yaw, thrust)
        i +=1
    rospy.loginfo("Bye!")

if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        pass
