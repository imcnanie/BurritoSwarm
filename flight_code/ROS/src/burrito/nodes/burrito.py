#
# burrito.py
#
# flightcode for burritocopter
# Josh Jacobs and Ian McNanie
# 2016
#

import socket
import math
import time
import json
import ast
import os
import rospy
# ROS movement functions
import velocity_goto

from threading import Thread

from dronekit import connect, VehicleMode, LocationGlobalRelative
from pymavlink import mavutil

from com import vehicleLink
from com import vehicleCommander


import utm

rospy.init_node('burrito')

SIMULATE = False

def status(message, server_comm):
    print message
    if server_comm:
        server_comm.stream_block[3] = message


class dropper:
    def __init__(self):
        self.dropped = False  #for later use in properly checking burrito deployment
        
    def deploy(self, dc):
        dc.channels.overrides['6'] = 500
        print "DROPPINGGGGG BRITOOO"
        self.dropped = True

        time.sleep(1.0)
        

class vehicleController:
    def __init__(self, veh_obj, bas_obj, copter_id):
        #self.dronekit_vc = connect('127.0.0.1:14550', wait_ready = True)
        self.brekin = velocity_goto.brekinIt(copter_id=copter_id, mavros_string="/mavros/copter"+copter_id)
        self.brekin.subscribe_pose_thread()


        self.dep = dropper()
        self.veh_obj = veh_obj
        self.bas_obj = bas_obj

    def mavlink_servo_move(self, num, pwm):
        self.mavServo = mavutil.mavlink.MAV_CMD_DO_SET_SERVO
        print "Sending Servo ", num, " PWM ", pwm

        #print mavutil.mavlink.MAV_COMP_ID_RETRACT

        if True:
            message = self.dronekit_vc.message_factory.command_long_encode(0,mavutil.mavlink.MAV_COMP_ID_IMU,self.mavServo,0,0,911,num,pwm,0,0,0)
            self.dronekit_vc.send_mavlink(message)
            self.dronekit_vc.flush()

    def take_off(self):
        time.sleep(0.1)
        self.brekin.set_velocity_publish(True)
        time.sleep(0.1)
        print "set mode"
        self.brekin.setmode(custom_mode="OFFBOARD")
        self.brekin.arm()
        print "ARMING"

        time.sleep(0.1)
        self.brekin.takeoff_velocity()

        status("TAKING OFF", self.bas_obj)


        print "Reached target altitude"
        

    def go_to(self, x, y, convert_to_utm=True):
        if convert_to_utm:
            utm_coords = utm.from_latlon(x, y)
            self.brekin.velocity_gps_goto(utm_coords[0], utm_coords[1],40.0)
        else:
            self.brekin.velocity_gps_goto(x, y,40.0)
        print "at gps, waiting"
        time.sleep(0.1)
        print "done"
        ## a_location = LocationGlobalRelative(x, y, self.alt)
        ## self.dronekit_vc.simple_goto(a_location)

        ## ## send_dat = []
        ## for i in range(3):
        ##     send_dat.append("")

        ## ## while True:
        ##     if self.veh_obj.message == "CANCEL" or self.veh_obj.message == "STOP":
        ##         return "CANCELLED"

        ## ##     if self.veh_obj.message == "CHANGE":
        ##         return "CHANGE"

        ## ##     initial_x = self.dronekit_vc.location.global_relative_frame.lat
        ##     initial_y = self.dronekit_vc.location.global_relative_frame.lon

        ## ##     self.bas_obj.stream_block[0] = str(initial_x)
        ##     self.bas_obj.stream_block[1] = str(initial_y)

        ## ##     if math.sqrt((initial_x - x)**2.0 + (initial_y - y)**2.0) < 0.0001:  # margin of error
        ##         return "ARRIVED"


    def deliver(self, coordinates, comm_obj = None):
        i_x = coordinates[0]
        i_y = coordinates[1]
        f_x = coordinates[2]
        f_y = coordinates[3]

        #h_x = self.dronekit_vc.location.global_relative_frame.lat
        #h_y = self.dronekit_vc.location.global_relative_frame.lon
        h_x = self.brekin.home_lat
        h_y = self.brekin.home_lon
        
        self.take_off()

        status("DELIVERING BURRITO...", self.bas_obj)

        while True:
            situation = self.go_to(f_x - i_x, f_y - i_y)

            if situation == "CHANGE":
                print "LOCATION CHANGED! ALTERING COURSE..."
                f_x = self.veh_obj.dists[0]
                f_y = self.veh_obj.dists[1]
                continue

            break

        if situation == "CANCELLED":
            status("ORDER CANCELLED!", self.bas_obj)
            time.sleep(0.5)

        else:
            status("LANDING", self.bas_obj)
            #self.dronekit_vc.mode = VehicleMode("LAND")
            self.brekin.land_velocity()
            self.brekin.set_velocity_publish(False)
            print "reimplement armed check"
            # while self.dronekit_vc.armed: 
            #     time.sleep(0.1)
 
            status("DROPPING BURRITO...", self.bas_obj)
            print "reimplement dropping"
            time.sleep(4)
            #self.dep.deploy(self.dronekit_vc)

            self.take_off()
            
        status("RETURN HOME...", self.bas_obj)
        situation = self.go_to(h_x, h_y, convert_to_utm=False)

        status("LANDING...", self.bas_obj)
        self.brekin.land_velocity()
        self.brekin.set_velocity_publish(False)
        #self.dronekit_vc.mode = VehicleMode("LAND")

        status("HOME!", self.bas_obj)
        time.sleep(0.1)


if __name__ == '__main__':


    vl = vehicleLink()
    vl.connect(ip = '127.0.0.1')
    vl.listen()

    bc = vehicleCommander()
    bc.connect(ip = '127.0.0.1', port = 5009)
    bc.start_streaming()

    #copter_id = raw_input("Copter ID: ")
    copter_id = raw_input("How many copters? ")
    vehicles = []
    for cops in range(int(copter_id)):
        v = vehicleController(vl, bc, str(cops+1))
        vehicles.append(v)

    while True:
        if SIMULATE:
            
            status("WAITING FOR HOME OFFSET...", bc)
    
            if True:
                while True:
                    if vl.message == "GO": break
                    time.sleep(0.01)
    
            vl.message = ""


            offset_lat = vl.dists[0]
            offset_lon = vl.dists[1]
            sim_lat, sim_lon = utm.to_latlon(vehicles[0].brekin.home_lat, vehicles[0].brekin.home_lon, 32, 'U')
            offset_lat = sim_lat - offset_lat
            offset_lon = sim_lon - offset_lon
            
        status("WAITING FOR COORDINATES...", bc)

        if True:
            while True:
                if vl.message == "GO": break
                time.sleep(0.01)

        vl.message = ""

        coord = []
        for i in range(4): coord.append(0.0)


        
        coord[2] = vl.dists[0]
        coord[3] = vl.dists[1]

        if SIMULATE:
            coord[2] = coord[2] + offset_lat
            coord[3] = coord[3] + offset_lon
        for cops in range(int(copter_id)):
            vehicles[cops].alt = 40     # FOR NOW

            status("PROCEEDING TO " + str(coord[2]) + ", " + str(coord[3]), bc)
            #v.brekin.home_lat
            #v.dronekit_vc.mode = VehicleMode("GUIDED")
            vehicles[cops].brekin.setmode(custom_mode="OFFBOARD")
            time.sleep(0.1)

            vehicles[cops].deliver(coord, bc) # BANG

            status("HOME!", bc)
            time.sleep(0.5)

        try:
            pass
        except KeyboardInterrupt:
            break


