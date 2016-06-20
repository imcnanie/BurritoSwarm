#!/usr/bin/env python  
import Tkinter as tk
import rospy
rospy.init_node('keyboard_teleop')

from geometry_msgs.msg import Twist, TwistStamped
import time

vx = 0.0
vy = 0.0
vz = 0.0
avz = 0.0

def callback(cmdVelocity):

        baseVelocity = Twist()

        baseVelocity.linear.x = cmdVelocity[0]
        baseVelocity.linear.y = cmdVelocity[1]
        baseVelocity.linear.z = cmdVelocity[2]
        baseVelocity.angular.z = cmdVelocity[3]
        #baseVelocity.angular(0,0,0)
        now = rospy.get_rostime()
        #baseVelocity.header.stamp.secs = now.secs
        #baseVelocity.header.stamp.nsecs = now.nsecs

        baseVelocityPub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
        baseVelocityPub.publish(baseVelocity)

def onKeyPress(event):
    global vx, vy, vz, avz
    if event.char == 'w':    
        vz = vz + 1.0
    if event.char == 'a':    
        avz = avz - 1.0
    if event.char == 's':    
        vz = vz - 1.0
    if event.char == 'd':    
        avz = avz + 1.0
    if event.char == 'i':    
        vy = vy + 1.0
    if event.char == 'j':    
        vx = vx - 1.0
    if event.char == 'k':    
        vy = vy - 1.0
    if event.char == 'l':    
        vx = vx + 1.0
    text.insert('1.0', 'vx: %d vy: %d \n' %(vx, vy))
    callback((vx,vy,vz,avz))


root = tk.Tk()
root.geometry('300x200')
text = tk.Text(root, background='black', foreground='white', font=('Comic Sans MS', 12))
text.pack()
root.bind('<KeyPress>', onKeyPress)
#root.mainloop()
while not rospy.is_shutdown():
    root.update_idletasks()
    root.update()
