import velocity_goto
import rospy
import time
import utm
rospy.init_node("land_test")
pv = velocity_goto.posVel(copter_id = "1")
pv.start_subs()
pv.subscribe_pose_thread()
time.sleep(0.1)
pv.start_navigating()
time.sleep(0.1)
print "set mode"
pv.setmode(custom_mode="MANUAL")
time.sleep(0.5)
pv.arm()
out = raw_input()
pv.setmode(custom_mode="POSCTL")
time.sleep(1.0)
pv.setmode(custom_mode="OFFBOARD")
#pv.takeoff_velocity(alt=7.0)
time.sleep(1.0)
print "out of takeoff"
utm_coords = utm.from_latlon(37.8733893, -122.3026196)
print "going to gps", utm_coords, "current: ", pv.get_lat_lon_alt()
#pv.update(utm_coords[0], utm_coords[1], 40.0)
pv.update(pv.cur_pos_x, pv.cur_pos_y, 7.0) 
pv.setmode(custom_mode="OFFBOARD")
#while not pv.reached:
#       time.sleep(0.025)
print out
print "at gps, waiting"
#time.sleep(2.0)
print "done"
copters = [pv]
velocity_goto.SmartRTL(copters)
#pv.land_velocity()
print "Landed!"

