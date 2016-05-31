#!/usr/bin/env python
import numpy as np
import rospy
import roslib
import tf
import PyKDL as kdl

# Messages
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Point, Quaternion

#roslib.load_manifest('odom_publisher')



gps_ekf_odom_pub = rospy.Publisher('/copter1/hellacopters/setpoint_odom/cmd_odom', Odometry, queue_size=10)
tf_br = tf.TransformBroadcaster()
publish_odom_tf = True
frame_id = '/odom'
child_frame_id = '/base_footprint'
# Covariance
P = np.mat(np.diag([0.0]*3))
def publish_odom():
    msg = Odometry()
    msg.header.stamp = rospy.Time.now()
    msg.header.frame_id = frame_id # i.e. '/odom'
    msg.child_frame_id = child_frame_id # i.e. '/base_footprint'
    
    msg.pose.pose.position = Point(10, 20, 5)
    msg.pose.pose.orientation = Quaternion(*(kdl.Rotation.RPY(0.5, 0.5, 0.5).GetQuaternion()))
    
    p_cov = np.array([0.0]*36).reshape(6,6)
    
    # position covariance
    p_cov[0:2,0:2] = P[0:2,0:2]
    # orientation covariance for Yaw
    # x and Yaw
    p_cov[5,0] = p_cov[0,5] = P[2,0]
    # y and Yaw
    p_cov[5,1] = p_cov[1,5] = P[2,1]
    # Yaw and Yaw
    p_cov[5,5] = P[2,2]
    
    msg.pose.covariance = tuple(p_cov.ravel().tolist())
    
    pos = (msg.pose.pose.position.x,
           msg.pose.pose.position.y,
           msg.pose.pose.position.z)
    
    ori = (msg.pose.pose.orientation.x,
           msg.pose.pose.orientation.y,
           msg.pose.pose.orientation.z,
           msg.pose.pose.orientation.w)
    
    # Publish odometry message
    gps_ekf_odom_pub.publish(msg)
    
    # Also publish tf if necessary
    if publish_odom_tf:
        tf_br.sendTransform(pos, ori, msg.header.stamp, msg.child_frame_id, msg.header.frame_id)
        

rospy.init_node("odom_test_pub")
        
hz = rospy.Rate(10)
while True:
    publish_odom()
    hz.sleep()
