import rospy
from mavros_msgs.srv import *

def send_mavlink_cmd(copter_id, cmd, broadcast, conf, param1, param2, param3, param4, param5, param6, param7):
	rospy.wait_for_service('/mavros/copter' + str(copter_id)+ '/cmd/command')
	try:
		sendDatCmd = rospy.ServiceProxy('/mavros/copter1/cmd/command', CommandLong)
		response = sendDatCmd(broadcast, cmd, conf, param1, param2, param3,param4, param5, param6, param7)
		print response
	except rospy.ServiceException, e:
		print "Service call failed: %s"%e

if __name__=="__main__":
	#Arming test
	send_mavlink_cmd(1, 400, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
