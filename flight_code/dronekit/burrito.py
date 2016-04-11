import socket
import math
import time
import json
import ast
import os

from threading import Thread

from dronekit import connect, VehicleMode, LocationGlobalRelative
from pymavlink import mavutil

from com import vehicleLink
from com import vehicleCommander


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
    def __init__(self, veh_obj, bas_obj):
        self.dronekit_vc = connect('127.0.0.1:14550', wait_ready = True)
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
        while not self.dronekit_vc.is_armable:
            status("WAITING FOR ARMABLE VEHICLE...", self.bas_obj)
            time.sleep(1)

        print "ARMING"

        self.dronekit_vc.mode    = VehicleMode("ALT_HOLD")
        self.dronekit_vc.armed   = True

        time.sleep(1.0)
        self.dronekit_vc.mode    = VehicleMode("GUIDED")

        while not self.dronekit_vc.armed:
            print " Waiting for arming..."
            time.sleep(1)

        status("TAKING OFF", self.bas_obj)

        self.dronekit_vc.simple_takeoff(self.alt)

        while True:
            #print " Altitude: ", 
            self.dronekit_vc.location.global_relative_frame.alt

            if self.dronekit_vc.location.global_relative_frame.alt >= self.alt*0.95:
                print "Reached target altitude"
                break
        

    def go_to(self, x, y):
        a_location = LocationGlobalRelative(x, y, self.alt)
        self.dronekit_vc.simple_goto(a_location)

        send_dat = []
        for i in range(3):
            send_dat.append("")

        while True:
            if self.veh_obj.message == "CANCEL" or self.veh_obj.message == "STOP":
                return "CANCELLED"

            if self.veh_obj.message == "CHANGE":
                return "CHANGE"

            initial_x = self.dronekit_vc.location.global_relative_frame.lat
            initial_y = self.dronekit_vc.location.global_relative_frame.lon

            self.bas_obj.stream_block[0] = str(initial_x)
            self.bas_obj.stream_block[1] = str(initial_y)

            if math.sqrt((initial_x - x)**2.0 + (initial_y - y)**2.0) < 0.0001:  # margin of error
                return "ARRIVED"


    def deliver(self, coordinates, comm_obj = None):
        i_x = coordinates[0]
        i_y = coordinates[1]
        f_x = coordinates[2]
        f_y = coordinates[3]

        h_x = self.dronekit_vc.location.global_relative_frame.lat
        h_y = self.dronekit_vc.location.global_relative_frame.lon

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
            self.dronekit_vc.mode = VehicleMode("LAND")

            while self.dronekit_vc.armed:
                time.sleep(0.1)
 
            status("DROPPING BURRITO...", self.bas_obj)
            self.dep.deploy(self.dronekit_vc)

            self.take_off()
  
        status("RETURN HOME...", self.bas_obj)
        situation = self.go_to(h_x, h_y)

        status("LANDING...", self.bas_obj)
        self.dronekit_vc.mode = VehicleMode("LAND")

        status("HOME!", self.bas_obj)
        time.sleep(0.1)


if __name__ == '__main__':
    vl = vehicleLink()
    vl.connect()
    vl.listen()

    bc = vehicleCommander()
    bc.connect(port = 5009)
    bc.start_streaming()

    v = vehicleController(vl, bc)

    while True:
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

        v.alt = 40     # FOR NOW

        status("PROCEEDING TO " + str(coord[2]) + ", " + str(coord[3]), bc)

        v.dronekit_vc.mode = VehicleMode("GUIDED")
        time.sleep(2.5)

        v.deliver(coord, bc) # BANG

        status("HOME!", bc)
        time.sleep(0.5)

        try:
            pass
        except KeyboardInterrupt:
            break


