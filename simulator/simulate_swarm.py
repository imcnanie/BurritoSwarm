import subprocess
import time
import os

print "How many copters to simulate: ",
key = raw_input()

cops = int(key)

def inplace_change(filename, old_string, new_string):
    s=open(filename).read()
    if old_string in s:
        print 'Changing Simulator Ports from "{old_string}" to "{new_string}"'.format(**locals())
        s=s.replace(old_string, new_string)
        f=open(filename, 'w')
        f.write(s)
        f.flush()
        f.close()
    else:
        print 'No occurances of "{old_string}" found.'.format(**locals())

for i in range(14, cops+14):

    filena = "copter"+str(i-13)
    if not os.path.exists((os.path.join(os.path.abspath(os.path.curdir),filena))):
        print "Creating Copter ",i-13        
        subprocess.call(["mkdir",filena])
        
        os.chdir(os.path.join(os.path.abspath(os.path.curdir),filena))
        
        subprocess.call(["git", "clone", "https://github.com/imcnanie/Firmware.git"])
        #working gazebo commit
	#os.chdir(os.path.join(os.path.abspath(os.path.curdir),"Firmware"))
        #subprocess.call(["git", "reset", "--hard", "8810ee33a4d44fbcc83606c175bff024ce937e68"])
	#os.chdir(os.path.join(os.path.abspath(os.path.curdir),".."))
        time.sleep(1)
        os.chdir(os.path.join(os.path.abspath(os.path.curdir),u'Firmware'))
        if i == 14:
            subprocess.call('cp ../flight_code/ROS/src/burrito/launch/px4_swarm.launch ../flight_code/ROS/src/mavros/mavros/launch/', shell=True)
            subprocess.call('cp ../flight_code/ROS/src/burrito/launch/node_swarm.launch ../flight_code/ROS/src/mavros/mavros/launch/', shell=True)
    else:
        print filena, " exists."
        os.chdir(os.path.join(os.path.abspath(os.path.curdir),filena+'/Firmware'))


    print "filena"
    old = str(14)
    new = str(i+1)
    path = os.path.abspath(os.path.curdir)
    print "THE PATH: ", path



    inplace_change(path+"/Vagrantfile", old+"556", new+"556")
    inplace_change(path+"/Vagrantfile", old+"560", new+"560")
    inplace_change(path+"/src/modules/mavlink/mavlink_main.cpp", old+"556", new+"556")
    inplace_change(path+"/posix-configs/SITL/init/rcS_gazebo_iris", old+"556", new+"556")
    inplace_change(path+"/posix-configs/SITL/init/rcS_gazebo_iris", old+"557", new+"557")
    inplace_change(path+"/posix-configs/SITL/init/rcS_gazebo_iris", old+"540", new+"540")
    inplace_change(path+"/posix-configs/SITL/init/rcS_jmavsim_iris", old+"556", new+"556")
    inplace_change(path+"/posix-configs/SITL/init/rcS_jmavsim_iris", old+"557", new+"557")
    inplace_change(path+"/posix-configs/SITL/init/rcS_jmavsim_iris", old+"540", new+"540")
    inplace_change(path+"/Tools/CI/MissionCheck.py", old+"540", new+"540")
    inplace_change(path+"/posix-configs/SITL/README.md", old+"550", new+"550")
    inplace_change(path+"/src/modules/mavlink/mavlink_main.cpp", old+"550", new+"550")
    inplace_change(path+"/Tools/sitl_run.sh", old+"560", new+"560")
    inplace_change(path+"/src/modules/simulator/simulator_mavlink.cpp", old+"560", new+"560")

    
    ## print "pysed -r \""+old+"560\" "+new+"560 "+path+"/Vagrantfile"
    ## subprocess.call("/usr/local/bin/pysed -r "+old+"556 "+new+"556 "+path+"/Vagrantfile", shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    ## subprocess.call("/usr/local/bin/pysed -r "+old+"560 "+new+"560 "+path+"/Vagrantfile", shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    ## subprocess.call("/usr/local/bin/pysed -r "+old+"556 "+new+"556 "+path+"/src/modules/mavlink/mavlink_main.cpp", shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    ## subprocess.call("/usr/local/bin/pysed -r "+old+"557 "+new+"557 "+path+"/posix-configs/SITL/init/rcS_jmavsim_iris", shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    ## subprocess.call("/usr/local/bin/pysed -r "+old+"540 "+new+"540 "+path+"/posix-configs/SITL/init/rcS_jmavsim_iris", shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    ## subprocess.call("/usr/local/bin/pysed -r "+old+"540 "+new+"540 "+path+"/Tools/CI/MissionCheck.py", shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    ## subprocess.call("/usr/local/bin/pysed -r "+old+"550 "+new+"550 "+path+"/posix-configs/SITL/README.md", shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    ## subprocess.call("/usr/local/bin/pysed -r "+old+"550 "+new+"550 "+path+"/src/modules/mavlink/mavlink_main.cpp", shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    ## subprocess.call("/usr/local/bin/pysed -r "+old+"560 "+new+"560 "+path+"/Tools/sitl_run.sh", shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    ## subprocess.call("/usr/local/bin/pysed -r "+old+"560 "+new+"560 "+path+"/src/modules/simulator/simulator_mavlink.cpp", shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    #subprocess.call("echo \"trip\"",shell=True)
    #subprocess.call('sed -e -i s/1' +old+ '556/' +new+ '556/g' +path+ '/Vagrantfile', shell=True)
    #subprocess.call('sed -e -i s/1' +old+ '560/' +new+ '560/g' +path+ '/Vagrantfile', shell=True)
    #subprocess.call('sed -e -i s/1' +old+ '556/' +new+ '556/g' +path+ '/src/modules/mavlink/mavlink_main.cpp ', shell=True)
    #subprocess.call('sed -e -i s/1' +old+ '557/' +new+ '557/g' +path+ '/posix-configs/SITL/init/rcS_jmavsim_iris', shell=True)
    #subprocess.call('sed -e -i s/1' +old+ '540/' +new+ '540/g' +path+ '/posix-configs/SITL/init/rcS_jmavsim_iris', shell=True)
    #subprocess.call('sed -e -i s/1' +old+ '540/' +new+ '540/g' +path+ '/Tools/CI/MissionCheck.py ', shell=True)
    #subprocess.call('sed -e -i s/1' +old+ '550/' +new+ '550/g' +path+ '/posix-configs/SITL/README.md ', shell=True)
    #subprocess.call('sed -e -i s/1' +old+ '550/' +new+ '550/g' +path+ '/src/modules/mavlink/mavlink_main.cpp', shell=True)
    #subprocess.call('sed -e -i s/1' +old+ '560/' +new+ '560/g' +path+ '/Tools/sitl_run.sh', shell=True)
    #subprocess.call('sed -e -i s/1' +old+ '560/' +new+ '560/g' +path+ '/src/modules/simulator/simulator_mavlink.cpp', shell=True)
    #print 'gnome-terminal '+ '--working-directory='+path+ '\" make posix_sitl_default jmavsim\" &'
    #print 'gnome-terminal '+ '--working-directory='+path+ ' -e \"no_sim=1 make posix_sitl_default gazebo\"'
    #subprocess.call('gnome-terminal '+ '--working-directory='+path+ ' -e \"../../make_sim.sh\"', shell=True)
    print 'gnome-terminal '+ '--working-directory='+path+ ' -e \"make posix_sitl_default jmavsim\"'
    subprocess.call('gnome-terminal '+ '--working-directory='+path+ ' -e \"make posix_sitl_default jmavsim"', shell=True)

    os.chdir(os.path.join(os.path.abspath(os.path.curdir),"../.."))
    

