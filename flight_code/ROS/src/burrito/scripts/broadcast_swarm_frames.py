#!/usr/bin/env python  
import roslib
#roslib.load_manifest('learning_tf')

from math import pi

import rospy
import rosnode
import tf
from nav_msgs.msg import Odometry
import geometry_msgs.msg
from sensor_msgs.msg import LaserScan
from std_msgs.msg import String, Header
print "broadcasting frames"

#roslib.load_manifest('odom_publisher')



class publish_copter_frame:
    def __init__(self,copter_name):
        self.dist = 10.0
        self.ang = 0.0
        self.get_home = True
        self.home_x = 0.0
        self.home_y = 0.0
        self.copter_name = copter_name
        
    def handle_pose(self,msg):
        #print "MESSAGE", dir(msg)
        pos = msg.pose.pose.position
        if self.get_home:
            self.home_x = pos.x
            self.home_y = pos.y
            self.get_home = False
        q = msg.pose.pose.orientation
        ang = q.x
        #print pos.x, self.home_x
        #print "X ",q.x, " Y ", q.y, " Z ", q.z, " W ", q.w
        br.sendTransform(( pos.x-self.home_x, pos.y-self.home_y,  pos.z),
                         (q.x, q.y, q.z, q.w),
                         rospy.Time.now(),
                         self.copter_name,
                         "fcu")


if __name__ == '__main__':
    rospy.init_node('px4_swarm_tfs_broadcaster')
    
    br = tf.TransformBroadcaster()
    rate = rospy.Rate(10.0)
    for copter_name in rosnode.get_node_names():
        if "mavros" in copter_name:
            pb = publish_copter_frame(copter_name)
            rospy.Subscriber(copter_name+'/global_position/local',
                             Odometry,
                             pb.handle_pose)
    
    while not rospy.is_shutdown():
        try:
            pass
        except KeyboardInterrupt:
            rospy.signal_shutdown("Keyboard Interrupt")

        rate.sleep()

    rospy.spin()
