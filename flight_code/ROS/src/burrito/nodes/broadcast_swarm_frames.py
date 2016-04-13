#!/usr/bin/env python  
import roslib
#roslib.load_manifest('learning_tf')

from math import pi

import rospy
import tf
from nav_msgs.msg import Odometry
import geometry_msgs.msg
from sensor_msgs.msg import LaserScan
from std_msgs.msg import String, Header
print "broadcasting"

#roslib.load_manifest('odom_publisher')

dist = 10.0
ang = 0.0
get_home = True
home_x = 0.0
home_y = 0.0
def handle_pose(msg):
    global dist, ang, get_home, home_x, home_y
    pos = msg.pose.pose.position
    if get_home:
        home_x = pos.x
        home_y = pos.y
        get_home = False
    q = msg.pose.pose.orientation
    ang = q.x
    print pos.x, home_x
    #print "X ",q.x, " Y ", q.y, " Z ", q.z, " W ", q.w
    br.sendTransform(( pos.x-home_x, pos.y-home_y,  pos.z),
                     (q.x, q.y, q.z, q.w),
                     rospy.Time.now(),
                     "f1",
                     "fcu")
    br.sendTransform(( 0, 0,  -float(dist)),
                     (0, 0, 0, q.w),
                     rospy.Time.now(),
                     "f2",
                     "f1")


   

if __name__ == '__main__':
    rospy.init_node('px4_tf_broadcaster')
    br = tf.TransformBroadcaster()
    rate = rospy.Rate(10.0)
    rospy.Subscriber('/mavros/global_position/local',
                     Odometry,
                     handle_pose)
    
    while not rospy.is_shutdown():
        try:
            pass
        except KeyboardInterrupt:
            rospy.signal_shutdown("Keyboard Interrupt")

        rate.sleep()

    rospy.spin()
