# HellaCopters
Swarming quadcopters and everything else that uses mavros!

# Installation
1. sudo apt-get install python-pip
2. sudo pip install utm
3. install mavros: https://github.com/mavlink/mavros/blob/master/mavros/README.md
4. cp px4_swarm.launch ../../mavros/mavros/launch/
5. cp node_swarm.launch ../../mavros/mavros/launch/
6. roslaunch solo_sim.launch
7. export SOLO_ROS_WS=<PATH_TO_flightcode/ROS_DIR> #ENV VAR used in solo_sim.launch and solo_swarm.launch
8. source $SOLO_ROS_WS/devel/setup.bash

![BurritoSwarm Screenshot](android/screenshots/burritoshot.png)
