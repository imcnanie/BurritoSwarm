import time

from threading import Thread

from com import vehicleCommander
from com import vehicleLink

class brito_com:
    def __init__(self):
        self.bl = vehicleLink()
        self.vc = vehicleCommander()

    def connect(self):
        self.bl.connect(port = 5009)
        self.bl.listen()

        self.last_status = ""

        while self.bl.data == "":
            time.sleep(0.025)

        self.vc.connect()

    def make_delivery(self, new_x, new_y):
        coords = []
        coords.append(str(new_x))
        coords.append(str(new_y))
        coords.append("GO")
        self.vc.send(coords)

    def make_change(self, new_x, new_y):
        coords = []
        coords.append(str(new_x))
        coords.append(str(new_y))
        coords.append("CHANGE")
        self.vc.send(coords)

    def threaded_status_listen(self):
        while True:
            #if self.bl.data: print self.bl.dists

            if not self.last_status == self.bl.data[3]:
                print self.bl.data[3]
                time.sleep(0.025)
                self.last_status = self.bl.data[3]

            time.sleep(0.025)

    def status_listen(self):
        st = Thread(target = self.threaded_status_listen, args = ())
        st.daemon = True
        st.start()


if __name__ == "__main__":
    b_com = brito_com()
    b_com.connect()
    b_com.status_listen()


 
