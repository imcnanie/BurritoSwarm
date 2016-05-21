import socket
import sys
import time
import wifi
import ping
import ssh

ASK_TIME =1
cont=True
cops = []
ports = {}

default_soloconf = """
[solo]

artooIp=10.1.1.1

soloIp=10.1.1.10

# Address to which RC packets are sent
rcDestPort=5005

# Address to which 'sysinfo' packet for the STM32 is sent
sysDestIp=%(artooIp)s
sysDestPort=5012

# Port to which 'pair request' packet for the STM32 is sent
pairReqDestPort=5013

# Port to which 'pair result' packet for the STM32 is sent
pairResDestPort=5014

# Port to which MAVLink packets for the STM32 are sent
mavDestPort=5015

# Port to connect to for button events (TCP)
buttonEventPort=5016

# Port to send button function config messages to
buttonFunctionConfigDestPort=5017

# Port to send set shot info messages to
setShotInfoDestPort=5018

# Port to send updater messages to
updaterDestPort=5019

# Port to which MAVLink packets are sent for all external systems
telemDestPort=14550

# TCP port where app server listens for connections
appServerPort=5502

# File where app_server saves connect app's IP address
appAddressFile=/var/run/solo_app.ip

# Artoo's serial ports

# Console is /dev/ttymxc0

# STM32
stm32Dev=/dev/ttymxc1
stm32Baud=115200

# Solo's serial ports

# Console is /dev/ttymxc0

# Pixhawk telemetry
telemDev=/dev/ttymxc1
telemBaud=921600
telemFlow=True

# Telemetry logging control
telemLogGap=1000000
telemLogDelayMax=100000
#telemLogDelayFile=/tmp/pkt_delays.csv

# Pixhawk RC
rcDsmDev=/dev/ttymxc2
rcDsmBaud=115200

# IP addresses from which Solo accepts RC packets
rcSourceIps=10.1.1.1,127.0.0.1

# Set system time from GPS when available
useGpsTime=True

# Throttle PWM mapping
pwmInMinThrottle=1000
pwmInMaxThrottle=2000
pwmOutMinThrottle=1000
pwmOutMaxThrottle=1900

# Rc timeout max
rcTimeoutUS=400000

# Telemetry display units (metric or imperial)
uiUnits=imperial

[pairing]
user_confirmation_timeout = 30.0
controller_link_port = 5501
wifi_connect_timeout = 5.0
connect_request_interval = 1.0
connect_ack_timeout = 0.5
solo_address_file = /var/run/solo.ip
button_filename = /dev/input/event0

[net]
ApEnable=True
StationEnable=False

[loggers]
keys=root,stm32,pix,pair,net,app,tlm,shot

[handlers]
keys=consoleHandler,sysLogHandler,sysLog2Handler

[formatters]
keys=simpleFormatter,syslogFormatter

[logger_root]
level=INFO
handlers=consoleHandler

[logger_stm32]
level=INFO
handlers=sysLogHandler
qualname=stm32
propagate=0

[logger_pix]
level=INFO
handlers=sysLogHandler
qualname=pix
propagate=0

[logger_pair]
level=INFO
handlers=sysLogHandler
qualname=pair
propagate=0

[logger_net]
level=INFO
handlers=sysLogHandler
qualname=net
propagate=0

[logger_app]
level=INFO
handlers=sysLogHandler
qualname=app
propagate=0

[logger_tlm]
level=INFO
handlers=sysLogHandler
qualname=tlm
propagate=0

[logger_shot]
level=INFO
handlers=sysLog2Handler
qualname=shot
propagate=0

[handler_consoleHandler]
class=StreamHandler
level=ERROR
formatter=simpleFormatter
args=(sys.stdout,)

[handler_sysLogHandler]
class=handlers.SysLogHandler
level=DEBUG
formatter=syslogFormatter
args=("/dev/log", handlers.SysLogHandler.LOG_LOCAL1)

[handler_sysLog2Handler]
class=handlers.SysLogHandler
level=DEBUG
formatter=syslogFormatter
args=("/dev/log", handlers.SysLogHandler.LOG_LOCAL2)

[formatter_simpleFormatter]
format=%(asctime)s %(name)-4s %(levelname)-8s %(message)s
datefmt=

[formatter_syslogFormatter]
format=%(name)s: %(message)s
datefmt=

[video]
videoMinFR=24
videoMaxFR=24
videoMinBR=800000
videoMaxBR=1800000
videoFRStep=5
videoBRStep=100000
varStreamRes=True
cropRecordRes=True
"""

def check_yesNo(resp):
	accepted_responses = ["Yes","yes","YES","y","Y"]
	if resp in accepted_responses:
		return True
	else:
		return False
def wait():
	time.sleep(ASK_TIME)

def exit():
	print "Exiting"
	sys.exit()
def wait_for_connected():
	messaged = False
	while True:
		try:
			if(ping.do_one("10.1.1.1",2) != None):
				break
			else:
				if messaged == False:
					print "Are you sure you're connected?"
					messaged = True
				

		except:
			if messaged == False:
				print "Are you sure you're connected?"
				messaged = True
	print "Connected!!"

def detect_ports(num_copters, silent=False):
	for i in range(14,14+num_copters):
  		sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    		port = int(str(i)+str(550))
    		sock.bind(("0.0.0.0", port))
    		sock.settimeout(.1)
    		try:
        		data, addr = sock.recvfrom(1)
        		return str(port)
    		except:
			pass
		if silent == False:		
			print "Make sure the solo is connected to the network."
		detect_ports(num_copters, silent=True)
		

def main():
	print "Hello! You've started the swarm install script. This script will guide you through setting up your swarm for flight.\n"
	wait()
	if(check_yesNo(raw_input("Are you ready to start setting up your swarm? (yes/no) ") == False)):
		exit()
	print "\nGreat, let's get started."
	wait()
	print "\nThe first step is to find the copter networks. Please wait while I scan for networks."
	while cont:
		copter_networks = [x.ssid for x in wifi.Cell().all("wlan0") if "SoloLink" in x.ssid]
		if copter_networks == []:
			if(check_yesNo(raw_input("\nNo networks found. Scan again? "))):
				continue
			else:
				exit()
		else:
			break
			
	print "\nI found these networks: "
	print copter_networks
	cops = raw_input("\nPlease enter the copters you would like to swarm in comma seperated form: a,b,c ")
	if(cops == ""):
		exit()
	cops = cops.replace(" ","").split(",")
	def_ports = []
	for i in range(len(cops)):
		def_ports.append(str(15550+i))
	print "\nThe next step is to detect which ports the copters are using to send mavlink_data"
	for cop in cops:
		print "\nPlease connect to " + cop +". You have 10 seconds."
		time.sleep(10)
		wait_for_connected()
		ports[cop] = detect_ports(len(cops))
	print "\nThe current port configuration on the copters is: "
	wait()
	for cop in ports.keys():
		print cop + " is on port " + ports[cop]
	wait()
	print "\nI am going to change the configuration to this: "
	wait()
	for cop in cops:
		print "\n" + cop + " will be assigned to port " + def_ports[cops.index(cop)]
 	if(check_yesNo(raw_input("\nContinue? ")) == False):
		exit()
	for cop in cops:
		if(ports[cop] != def_ports[cops.index(cop)]):
			print "\nPlease connect to " + cop +". You have 10 seconds."
			time.sleep(10)
			wait_for_connected()
			client = ssh.ssh_instance()
			client.connect("10.1.1.10")
			soloconf = client.command("cat /etc/sololink.conf")
			soloconf = soloconf.replace("telemDestPort=14550","telemDestPort="+def_ports[cops.index(cop)])
			client.command_blind('echo "' + new_soloconf + '" > /etc/sololink.conf')
			print "echo '" + soloconf + "' > /etc/sololink.conf"
			client.command_blind("md5sum /etc/sololink.conf > /etc/sololink.conf.md5")
			client.command_blind("reboot")
			client = ssh.ssh_instance()
			client.connect("10.1.1.1")
			artooconf = client.command("cat /etc/sololink.conf")
			artooconf = artooconf.replace("telemDestPort=14550","telemDestPort="+def_ports[cops.index(cop)])
			client.command_blind('echo "' + new_soloconf + '" > /etc/sololink.conf')
			client.command_blind("md5sum /etc/sololink.conf > /etc/sololink.conf.md5")
			client.command_blind("reboot")

		print "\nCopter " + cop + " finished."
	wait()
	f = open("swarm_info",'rw')
	text = ""
	for cop in cops:
		text = text + cop+":"+def_ports[cops.index[cop]]+"\n"
	f.write(text)
	f.close()
	print "\nYour settings have been written to the file swarm_info"
	wait()
	print "\nAll done! Remember to swarm safely."
	
		
		
if __name__=="__main__":
	main()
