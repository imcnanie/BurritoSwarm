import socket
import time
import json
import ast

from threading import Thread

class vehicleCommander:
    def __init__(self):
        self.modes = []
        self.data = ""
        self.raw_data = ""

        self.stream_interrupt = False
        
        self.stream_block = []
        for i in range(6):
            self.stream_block.append("")

        self.stream_block[0] = "0.0"
        self.stream_block[1] = "0.0"

    def connect(self, ip = '10.1.1.10', port = 5008):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        self.sock.connect((ip, port))

    def thread_send(self, data):
        message = "%%" + json.dumps(data) + "$$"
        self.sock.send(message)

    def send(self, data):
        self.stream_interrupt = True
        message = "%%" + json.dumps(data) + "$$"
        self.sock.send(message)
        data = ""
        message = ""

    def stream(self):
        while True:
            self.thread_send(self.stream_block)
            time.sleep(0.015)

            if self.stream_interrupt:
                time.sleep(1.5)
                self.stream_interrupt = False

    def start_streaming(self):
        st = Thread(target = self.stream, args = ())
        st.daemon = True
        st.start()

    def cancel(self):
        filler = ["0.0", "0.0", "CANCEL"]
        self.send(filler)


class vehicleLink:
    def __init__(self):
        self.modes = []
        self.stuff = ""
        self.data = ""
        self.raw_data = ""

        # EXPECTED MESSAGE FORMATTING:
        # 
        # 0: self.dists[0] ~ final x float
        # 1: self.dists[1] ~ final y float
        # 2: self.message ~ "GO", "STOP", "CANCEL", "CHANGE"
        # 3: self.status ~ status message from drone

        self.dists = []
        self.message = ""
        self.status = ""

        for i in range(2):
            self.dists.append(0.0)

        self.alt = 0

    def connect(self, ip = '', port = 5008):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #self.sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)

        self.sock.bind((ip, port))

    def strip(self, fullString):
        newString = fullString[(fullString.index("%%")+2):fullString.index("$$")]

        if True:
            self.stuff = ast.literal_eval(newString)

        return self.stuff

    def listener_thread(self):
        self.data = ""
        self.raw_data = ""

        while True:
            while True:
                self.raw_data, new_addr = self.sock.recvfrom(1024)

                time.sleep(0.01)

                if "$$" in self.raw_data and "%%" in self.raw_data:
                    self.data = self.strip(self.raw_data)

                    for i in range(2):
                        self.dists[i] = float(self.data[i])

                    if len(self.data) > 2:
                        self.message = self.data[2]
                    else:
                        self.message = "GO" 

                    break

                else:
                    print "OOPS!", self.raw_data


    def listen(self):
        l_t = Thread(target=self.listener_thread, args=())
        l_t.daemon = True
        l_t.start()

