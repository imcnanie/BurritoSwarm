#!/usr/bin/env python

import time
import socket
import struct
import threading
import sys

sys.path.insert(0, '/usr/bin')

import btn_msg

class buttonHandler:
    def __init__(self):
        self.format = 1
        self.button = ""
        self.destroy = False
        self.buttonState = {'A' : ["Released",""],
                            'B' : ["Released",""],
                            'Power' : ["Released",""],
                            'Fly' : ["Released",""],
                            'RTL' : ["Released",""],
                            'Loiter' : ["Released",""],
                            'Preset1' : ["Released",""],
                            'Preset2' : ["Released",""],
                            'CameraClick' : ["Released",""]}

        self.lastButton = ""
        self.update = False

	host = "10.1.1.1"
        port = 5016

        print "CONNECTING..."
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        print ""
        print "CONNECTED! "

    def in_thread(self):
        while not self.destroy:
            msg = btn_msg.recv(self.sock)

	    if msg is None:
                print "Naw"
                break
            else:
                if True:
                    self.button = btn_msg.ButtonName[msg[1]]
                    self.update = True

                    if msg[2]==0:
                        self.buttonState[self.button][0] = "Pressed"

                    if msg[2]==1 or msg[2]==2:
                        self.buttonState[self.button][0] = "Released"
                        self.buttonState[self.button][1] = ""

                    if msg[2]==3:
                        self.buttonState[self.button][1] = "Short"

                    if msg[2]==4:
                        self.buttonState[self.button][1] = "Long"

                    if msg[2]==5:
                        self.buttonState[self.button][1] = "Super Long"

                    if msg[2]==6:
                        self.buttonState[self.button][1] = "Spam"

            btn_msg.msg_buf_long = 0

    def startListening(self):
        in_id = threading.Thread(target=self.in_thread, args=())
        in_id.daemon = True
        in_id.start()

    def changed(self):
        if self.update:
            self.update = False
            return True
        else:
            return False


if __name__ == "__main__":
    bh = buttonHandler()
    bh.startListening()

    while True:
        if bh.changed():
            print bh.button
            print ""
            print bh.buttonState


# POSSIBLE RETURNS:
#
#  A
#  B
#  Power
#  Fly
#  RTL
#  Loiter
#  Preset1
#  Preset2
