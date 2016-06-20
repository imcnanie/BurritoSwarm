#!/bin/sh -x
# Modified version of catkin template/python_distutils_install.sh.in

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

echo_and_run cd "/home/bjork/BurritoSwarm/flight_code/ROS/src/mavlink/pymavlink"

# snsure that Python install destination exists
echo_and_run mkdir -p "$DESTDIR/home/bjork/BurritoSwarm/flight_code/ROS/devel/lib/python2.7/dist-packages"

# Note that PYTHONPATH is pulled from the environment to support installing
# into one location when some dependencies were installed in another
# location, ros/catkin#123.
echo_and_run /usr/bin/env \
    PYTHONPATH="/home/bjork/BurritoSwarm/flight_code/ROS/devel/lib/python2.7/dist-packages:/home/bjork/BurritoSwarm/flight_code/ROS/build/mavlink/lib/python2.7/dist-packages:$PYTHONPATH" \
    "/usr/bin/python2" \
    "/home/bjork/BurritoSwarm/flight_code/ROS/src/mavlink/pymavlink/setup.py" \
    build --build-base "/home/bjork/BurritoSwarm/flight_code/ROS/build/mavlink/pymavlink" \
    install \
    $DESTDIR_ARG \
    --install-layout=deb --prefix="/home/bjork/BurritoSwarm/flight_code/ROS/devel"
#--install-scripts="/home/bjork/BurritoSwarm/flight_code/ROS/devel/"

