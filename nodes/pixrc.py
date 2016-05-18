#
# Modular Pixrc
# William Peale - 2016
#

#!/usr/bin/env python

#import argparse
import datetime
import errno
import os
#import serial
#import simple_stats
import socket
import struct
import sys
import threading
import time

# RC packets are received as a timestamp, sequence number, then channel data.
# * timestamp is microseconds since some epoch (64 bits)
# * sequence simply increments each packet (16 bits) and can be used to detect
#   missed or out of order packets.
# * channel data is a PWM value per channel (16 bits)
#
# All data is received little-endian. A typical packet is as follows (8
# channels, all 1500):
#
#        timestamp         seq   ch0   ch1   ch2   ch3   ch4   ch5   ch6   ch7
# |----- 3966001072 ----|  3965  1500  1500  1500  1500  1500  1500  1500  1500
# b0 5f 64 ec 00 00 00 00 7d 0f dc 05 dc 05 dc 05 dc 05 dc 05 dc 05 dc 05 dc 05

# DSM is sent in 16-byte chunks, each contain 8 2-byte words:
#
# Word  Data
# 0     0x00AB (magic)
# 1..7  (chNum << 11) | (chData & 0x7ff)
#
# For more than 7 channels, another packet is sent, starting with the magic.
# 16 bytes are always sent; unused channel slots are filled with 0xffff.
#
# Each word is sent big-endian. A typical byte stream might be as follows
# (8 channels, all =750):
#
# magic --0-- --1-- --2-- --3-- --4-- --5-- --6--
# 00 ab 02 ee 0a ee 12 ee 1a ee 22 ee 2a ee 32 ee
#
# magic --7-- --x-- --x-- --x-- --x-- --x-- --x--
# 00 ab 3a ee ff ff ff ff ff ff ff ff ff ff ff ff
#
# Note that the arriving UDP packet is PWM values in microseconds.
# Those are converted to 11-bit channel values by shifting down one bit.
rcChansOut = None

class controller():
	def __init__(self, sim=False):
		self.CHANNEL_BITS = 11
		self.CHANNEL_MASK = 0x7ff

		self.SOCKET_TIMEOUT = 0.4
		self.DSM_INTERVAL = 0.020
		self.OUTPUT_TRUE = sim
		self.dsmBeat = 0
		self.rcBeat = 0

		# Debug only; enable/disable sending packets to Pixhawk
		self.DSM_SEND_ENABLE = True

		self.rcChansOut = None
		self.rcFailsafeChans = [ 0, 1500, 1500, 1500 ]
		self.pollSleep = max(self.DSM_INTERVAL, self.SOCKET_TIMEOUT) * 5
				

		self.rcDsmDev = "/dev/ttymxc2"
		self.rcDsmBaud = 115200

		# Only accept RC packets from one of these
		self.rcSourceIps = ["10.1.1.1","127.0.0.1"]

		# RC packets arrive on this port
		self.rcDestPort = 5005

                #os.nice(-20)

	    	self.rcDsmLock = threading.Lock()
                print " yeah ", self.OUTPUT_TRUE
	    	if False: #self.DSM_SEND_ENABLE and (not self.opts.sim or not self.OUTPUT_TRUE):
    			self.sender = threading.Thread(name = "dsmSend", target = self.dsmSend, args = (self.rcDsmDev, self.rcDsmBaud))
    			self.sender.daemon = True
    			self.sender.start()

		self.receiver = threading.Thread(name = "rcReceive", target = self.rcReceive, args = (self.rcDestPort, ))
		self.receiver.daemon = True
		self.receiver.start()

	def start(self):
   		self.oldDsmBeat = self.dsmBeat
    		self.oldRcBeat = self.rcBeat
    		time.sleep(self.pollSleep)

                #print self.channel_list

    		if False: #self.DSM_SEND_ENABLE and (not self.opts.sim or not self.OUTPUT_TRUE):
        		if self.dsmBeat == self.oldDsmBeat:
            			print "DSM thread dead, exiting."
            			sys.exit(1)
    		if self.rcBeat == self.oldRcBeat:
        		print "RcReceive thread dead, exiting."
        		sys.exit(1)
		
	def rcUnpack(self, packedData):
	    	"""Unpack RC packet.

	    	Returns a tuple (timestamp, sequence, channels[]).
	   	"""
	    	# Length of received packet determines how many channels there
	    	# are: packet is 8 + 2 + (2 * numChans) bytes
	    	# Sanity-check received packet
	    	dataLen = len(packedData)
	    	if dataLen < 10 or (dataLen & 1) != 0:
			print "rcUnpack: malformed packet received (length = %d)"% (dataLen)
			return None
	    	# require 4..14 channels
	    	numChans = (dataLen - 10) / 2
	    	if numChans < 4 or numChans > 14:
			print "rcUnpack: malformed packet received (%d channels)" % (numChans)
			return None
	    	timestamp, sequence = struct.unpack("<QH", packedData[:10])
	    	channels = [ ]
	    	for i in range(10, dataLen, 2):
			channels.extend(struct.unpack("<H", packedData[i:i+2]))

	    	#if channels is not None and self.opts.show_rc:
		#	print channels


	    	return timestamp, sequence, channels


	def dsmPack(self, channels):
	    	"""Pack channels into DSM packet."""
	    	if channels is None:
			return None
	    	dsmPacket = ""
	    	channelsLeft = len(channels)
	   	channelNum = 0
	   	while channelsLeft > 0:
			dsmPacket += struct.pack(">H", 171)
		# pack 7 channels before needing another magic		
			for c in range(0, 7):
		    		if channelsLeft > 0:
		        		# channel value is 1000...2000
		        		# needs to be 174...1874
		        		value = channels[channelNum]   # 1000...2000

		       			value = value * 1700 / 1000 - 1526
		        		if(value < 0):
		            			value = 0
		        		if(value > 2000):
		            			value = 2000;

		        		chan = (channelNum << self.CHANNEL_BITS) | (value & self.CHANNEL_MASK)
		        		dsmPacket += struct.pack(">H", chan)
		        		channelsLeft -= 1
		        		channelNum += 1
		    		else:
		        		dsmPacket += struct.pack(">H", 65535)
		return dsmPacket


	def dsmSend(self, devName, baudRate):

       
            print self.OUTPUT_TRUE, "test"
            if True: #self.opts.sim or self.OUTPUT_TRUE:
	        print("not sending to pixhawk")
            else:
	    	print ("opening %s at %d") % (devName, baudRate)
	    	try:
	            self.serialPort = serial.Serial(devName, baudRate)
	    	except serial.SerialException as excOpen:
		    print "Could not open serial port."                    
		    return

	    pixOutLogger = None
	    
	  
	    while True:	
		self.dsmBeat += 1
		self.rcDsmLock.acquire()		
		dsmBytes = self.dsmPack(self.rcChansOut)		
		self.rcDsmLock.release()
		if dsmBytes is None:
		    print("dsmSend: None")
		else:
		   print "dsmSend: %s" % ([hex(ord(c)) for c in dsmBytes].__str__())

		if False: #dsmBytes is not None and (not self.opts.sim and not self.OUTPUT_TRUE):
		    if pixOutLogger:
		        pixOutLogger.log_packet(dsmBytes)
		    self.serialPort.write(dsmBytes)

		if dsmBytes is not None and False: #self.opts.show_raw:
		    print dsmBytes
		time.sleep(self.DSM_INTERVAL)


	def rcReceive(self, udpPortNum):

	    print("rcReceive running")

	    #stats = simple_stats.SimpleStats()

	    pixInLogger = None
	    #pixInLogger = logd.PixInLogger()

	    # Open socket
	    print "rcReceive: listening on port %d" % (udpPortNum)
	    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	    sock.bind(("", udpPortNum))

	    # We require the timestamp on the RC packet to be greater than the
	    # previous one, or the packet is dropped. However, if we see enough "old"
	    # packets in a row, we assume the timestamp has restarted, and start
	    # accepting packets again.
	    rcTimePrev = None
	    oldPktCnt = 0
	    oldPktRestart = 5 # 100 msec at 20 msec / packet

	    nextWarnTime = None
	    warnInterval = datetime.timedelta(seconds = 5)

	    # The sequence number is used to detect and count dropped packets. We
	    # increment dropCnt for "small" gaps in the sequence (incrementing it by
	    # the number of packets dropped), and increment discCnt for "large" gaps
	    # (discontinuities). goodCnt is incremented for packets receive in sequence.
	    rcSeqPrev = None
	    dropCnt = 0
	    goodCnt = 0
	    discCnt = 0
	    discGap = 5

	    # Packets received less than this much time after the previous one are
	    # discarded, under the assumption that it is part of a burst. The last
	    # packet in a burst is discarded (even if it is not old), and then the
	    # next one is the first used.
	    pktIntervalMin = datetime.timedelta(milliseconds=2)

	    # Log packet statistics periodically
	    logInterval = datetime.timedelta(seconds = 10)
	    logTime = datetime.datetime.now() + logInterval

	    rcBeatTime = None
	    rcBeatIntervalMax = datetime.timedelta(seconds = 0.040)
	    nowDsm = None
	    sock.settimeout(self.SOCKET_TIMEOUT)
	    while True:
		self.rcBeat += 1
		# The following rcBeatInterval stuff was added because we were getting
		# "errors" when checking for rcBeat to increment at least every 1.5
		# times the socket timeout. The error check was loosened up and the
		# interval measurement added to see just how bad it is.
		if rcBeatTime is not None:
		    rcBeatInterval = datetime.datetime.now() - rcBeatTime
		    if rcBeatIntervalMax < rcBeatInterval:
		        rcBeatIntervalMax = rcBeatInterval
		        print "rcBeatIntervalMax is now %f seconds" % (rcBeatIntervalMax.total_seconds())
		rcBeatTime = datetime.datetime.now()
		try:
		    rcBytes, addr = sock.recvfrom(256)
		except socket.timeout:
		    now = datetime.datetime.now()
		    if nextWarnTime is None or now >= nextWarnTime:
		        print("socket timeout: sending failsafe packet")
		        nextWarnTime = now + warnInterval
		    rcTime = 0
		    rcSeq = 0
		    rcChans = self.rcFailsafeChans
		    rcTimePrev = rcTime
		else:
		    nowDsmLast = nowDsm
		    nowDsm = datetime.datetime.now()
		    now = nowDsm
		    if pixInLogger:
		        pixInLogger.log_packet(rcBytes)
		    if nowDsmLast is not None:
		        delta_us = (nowDsm - nowDsmLast).total_seconds() * 1000000
		        #stats.update(delta_us)
		    if nextWarnTime is not None:
		        print("received packet after timeout")
		        nextWarnTime = None
		    # only accept RC packets from Artoo
		    if not addr[0] in self.rcSourceIps:
		        print "packet from %s ignored" % (addr[0])
		        continue
		    rcTime, rcSeq, rcChans = self.rcUnpack(rcBytes)
		    # Check sequence - just require that the timestamp is increasing.
		    # But... if we see enough "old" packets in a row (oldPktRestart),
		    # we assume the timestamp has started over and start accepting
		    # packets again.
		    if rcTimePrev is not None and \
		       rcTime <= rcTimePrev and \
		       oldPktCnt < oldPktRestart:
		        print "old packet ignored (%s <= %s)" % (rcTime.__str__(), rcTimePrev.__str__())
		        oldPktCnt += 1
		        continue
		    rcTimePrev = rcTime
		    oldPktCnt = 0

		    # The packet is later than the previous one; look for missed
		    # packets (diagnostic).
		    # 64K packets wraps after about 21m 50s; test with wrap at 256 (5s)
		    rcSeqMax = 65536
		    #rcSeqMax = 256
		    #rcSeq = rcSeq & (rcSeqMax - 1)
		    if rcSeqPrev is None:
		        rcSeqPrev = rcSeq
		    else:
		        # mod-64K subtract
		        gap = rcSeq - rcSeqPrev
		        if gap < 0:
		            gap += rcSeqMax
		        if gap == 1:
		            goodCnt += 1
		        else:
		            if gap <= discGap:
		                dropCnt += (gap - 1)
		            else:
		                discCnt += 1
		        
		        rcSeqPrev = rcSeq


		if now > logTime:
		    #count = stats.count()
		    #if count > 0:
		    #    logger.info("n=%d avg=%0.0f min=%0.0f max=%0.0f stdev=%0.1f",
		    #                count, stats.average(),
		    #                stats.min(), stats.max(), stats.stdev())
		    #stats.reset()
		    logTime += logInterval

		# Make new RC data available to dsmSend thread. rcChans was either set
		# to the new RC data if we got it, or to the failsafe packet if not.
		self.rcDsmLock.acquire()
		self.rcChansOut = rcChans
		self.rcDsmLock.release()


if __name__ == '__main__':
	solo_controller = controller(sim=True)
	solo_controller.start()



