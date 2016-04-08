from klein import Klein
import britoProxy
import ast

app = Klein()
bc = britoProxy.brito_com()
bc.connect()
bc.status_listen()

delivery_queue = []

@app.route('/deliver/<new_delivery>')
def pg_user(request, new_delivery):
    delivery_queue.append(new_delivery)

    lat,lon = ast.literal_eval(new_delivery)

    bc.make_delivery(lat,lon)

    return 'Delivering to coordinates %s!' % (new_delivery,)

@app.route('/status')
def pg_status(request):
    return 'Copter Status: ' + str(bc.bl.data)

@app.route('/track')
def pg_track(request):
    return 'Deliveries: ' + str(delivery_queue)

@app.route('/cancel')
def pg_cancel(request):
    dummy = ["0.0","0.0","CANCEL"]
    bc.vc.cancel()
    return 'Canceled delivery'

@app.route('/change/<new_coord>')
def pg_change(request, new_coord):
    delivery_queue.append(new_delivery)

    lat,lon = ast.literal_eval(new_delivery)

    bc.make_change(lat,lon)

    return 'Delivering to new coordinate %s!' % (new_delivery,)

app.run("0.0.0.0", 8080)
