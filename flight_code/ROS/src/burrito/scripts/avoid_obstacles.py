#!/usr/bin/env python
import time
import rospy
import mavros
from threading import Thread
from mavros import setpoint as SP
from geometry_msgs.msg import Twist, TwistStamped, Vector3

class Move:
    def __init__(self):
        self.vx=0.0
        self.vx_min=-1.0
        self.vx_max=1.0

        self.vy=0.0
        self.vy_min=-1.0
        self.vy_max=1.0

        self.vz=0.0
        self.vz_min=-1.0
        self.vz_max=1.0

        self.avz=0.0
        self.avz_min=-1.0
        self.avz_max=1.0

        self.magnitude=1.0
        self.navigate_rate=30 # navigate thread will run at 30hz
        self.override_nav=False

        self.pub_cmd_vel = rospy.Publisher(mavros.get_topic('setpoint_velocity', 'cmd_vel'), 
                                       TwistStamped, queue_size=10)

    def navigate(self):
        # Listens to input from /cmd_vel topic, masks with updates from velocity_mask(),
        # and publishes velocity setpoints to /mavros/setpoint_velocity/cmd_vel

        rate = rospy.Rate(self.navigate_rate)

        vel_msg = TwistStamped(
                  header=SP.Header(
                    frame_id="base_footprint",  # doesn't matter
                    stamp=rospy.Time.now()),    # stamp should update
                  )

        while not rospy.is_shutdown():
            if self.vx > self.vx_max:
                self.vx = self.vx_max
            if self.vx < self.vx_min:
                self.vx = self.vx_min
            if self.vy > self.vy_max:
                self.vy = self.vy_max
            if self.vy < self.vy_min:
                self.vy = self.vy_min

            if not self.override_nav:
                vel_msg.twist.linear  = Vector3(self.vx*self.magnitude,
                                                self.vy*self.magnitude,
                                                self.vz*self.magnitude)

                vel_msg.twist.angular = Vector3(0,
                                                0,
                                                self.avz*self.magnitude)
            self.pub_cmd_vel.publish(vel_msg)
            rate.sleep()

    def listen_and_move(self):
        # Starts navigate thread
        t = Thread(target = self.navigate, args = ())
        t.daemon = True
        t.start()

    def update_velocity(self, cmd_vel_msg):
        # Updates navigate's setpoints
        print "Got Velocity setpoint"
        self.vx = cmd_vel_msg.linear.x
        self.vy = cmd_vel_msg.linear.y
        self.vz = cmd_vel_msg.linear.z
        self.avz = cmd_vel_msg.angular.z
    def cmd_vel_listener(self):
        rospy.Subscriber("cmd_vel", Twist, self.update_velocity)

    def velocity_mask(self, vx_min=-1, vx_max=1, vy_min=-1, vy_max=1):
        # Write a mask over the velocity range, which removes
        # a certain range of velocities user can send. Scaled
        # between -1 and 1.
        self.vx_min=-1
        self.vx_max=1
        self.vy_min=-1
        self.vy_max=1

if __name__ == '__main__':
    rospy.init_node('avoid_obstacles', anonymous=True)
    mavros.set_namespace('/mavros')
    move = Move()
    move.listen_and_move()
    while not rospy.is_shutdown():
        move.cmd_vel_listener()
        rospy.spin()
