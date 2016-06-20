#!/bin/sh

if [ -n "$DESTDIR" ] ; then
    case $DESTDIR in
        /*) # ok
            ;;
        *)
            /bin/echo "DESTDIR argument must be absolute... "
            /bin/echo "otherwise python's distutils will bork things."
            exit 1
    esac
    DESTDIR_ARG="--root=$DESTDIR"
fi

echo_and_run() { echo "+ $@" ; "$@" ; }

echo_and_run cd "/home/bjork/BurritoSwarm/flight_code/ROS/src/mavros/mavros"

# Note that PYTHONPATH is pulled from the environment to support installing
# into one location when some dependencies were installed in another
# location, #123.
echo_and_run /usr/bin/env \
    PYTHONPATH="/home/bjork/BurritoSwarm/flight_code/ROS/install/lib/python2.7/dist-packages:/home/bjork/BurritoSwarm/flight_code/ROS/build/mavros/lib/python2.7/dist-packages:$PYTHONPATH" \
    CATKIN_BINARY_DIR="/home/bjork/BurritoSwarm/flight_code/ROS/build/mavros" \
    "/usr/bin/python" \
    "/home/bjork/BurritoSwarm/flight_code/ROS/src/mavros/mavros/setup.py" \
    build --build-base "/home/bjork/BurritoSwarm/flight_code/ROS/build/mavros" \
    install \
    $DESTDIR_ARG \
    --install-layout=deb --prefix="/home/bjork/BurritoSwarm/flight_code/ROS/install" --install-scripts="/home/bjork/BurritoSwarm/flight_code/ROS/install/bin"
