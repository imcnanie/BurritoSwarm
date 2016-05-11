from klein import Klein
#import britoProxy
import ast
import velocity_goto
import rospy
import time
import utm



app = Klein()
#bc = britoProxy.brito_com()
#bc.connect()
#bc.status_listen()

delivery_queue = []

@app.route('/deliver/<new_delivery>')
def pg_user(request, new_delivery):
    delivery_queue.append(new_delivery)

    lat,lon = ast.literal_eval(new_delivery)


    rospy.init_node("land_test")
    pv = velocity_goto.posVel(copter_id = "1")
    pv.start_subs()
    pv.subscribe_pose_thread()
    time.sleep(0.1)
    pv.start_navigating()
    time.sleep(0.1)
    print "set mode"
    time.sleep(0.5)
    pv.setmode(custom_mode="")
    time.sleep(2.0)
    pv.arm()
    #out = raw_input()
    time.sleep(2.0)
    pv.setmode(custom_mode="OFFBOARD")
    pv.takeoff_velocity(alt=6.0)
    time.sleep(0.5)
    print "out of takeoff"
    utm_coords = utm.from_latlon(lat,lon)
    #utm_coords = utm.from_latlon(37.873308606981595,-122.30257440358399) #(37.87328$
    print "going to gps", utm_coords, "current: ", pv.get_lat_lon_alt()
    pv.update(utm_coords[0], utm_coords[1], 7.0)
    #pv.update(pv.cur_pos_x, pv.cur_pos_y, 7.0) 
    pv.setmode(custom_mode="OFFBOARD")
    while not pv.reached:
           time.sleep(0.025)
    #print out
    print "at gps, waiting"
    #time.sleep(2.0)
    print "done"
    #pv.land_velocity()
    pv.setmode(custom_mode="AUTO.LAND")
    #copters = [pv]
    #velocity_goto.SmartRTL(copters)
    #pv.land_velocity()
    print "Landed!"




    #bc.make_delivery(lat,lon)

    return 'Delivering to coordinates %s!' % (new_delivery,)

@app.route('/status')
def pg_status(request):
    return 'Copter Status: ' #+ str(bc.bl.data)

@app.route('/track')
def pg_track(request):
    return 'Deliveries: ' + str(delivery_queue)

@app.route('/cancel')
def pg_cancel(request):
    dummy = ["0.0","0.0","CANCEL"]
    #bc.vc.cancel()
    return 'Canceled delivery'

@app.route('/change/<new_coord>')
def pg_change(request, new_coord):
    delivery_queue.append(new_delivery)

    lat,lon = ast.literal_eval(new_delivery)

    #bc.make_change(lat,lon)

    return 'Delivering to new coordinate %s!' % (new_delivery,)

app.run("0.0.0.0", 8080)
