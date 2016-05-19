# Written by Josh Jacobs

import paramiko

def flash():
    print "Enter your IP on the artoo network:",
    key = raw_input()

    print "Flashing IP..."

    pcc = paramiko.Transport(("10.1.1.1", 22))
    pcc.connect(username = "root", password = "TjSDBkAu")

    sesh = pcc.open_channel(kind = 'session')

    cmd = "echo \'"+key+"\' > /var/run/solo.ip"

    sesh.exec_command(cmd)
    #sesh.exec_command("init 3")
    #sesh.exec_command("init 4")

    sesh.close()
    pcc.close()

if __name__ == "__main__":  
    flash()
