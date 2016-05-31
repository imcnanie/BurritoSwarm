import socket

UDP_IP = "0.0.0.0"
UDP_PORT = 16550

for i in range(15,20):
    sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    port = int(str(i)+str(550))
    print port
    sock.bind((UDP_IP, port))
    sock.settimeout(.1)
    try:
	data, addr = sock.recvfrom(1)
	print "Solo on port " + str(i) + " ok"
    except:
	print "Solo on port " + str(i) + " not recving"
