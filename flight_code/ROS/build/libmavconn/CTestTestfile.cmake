# CMake generated Testfile for 
# Source directory: /home/bjork/BurritoSwarm/flight_code/ROS/src/mavros/libmavconn
# Build directory: /home/bjork/BurritoSwarm/flight_code/ROS/build/libmavconn
# 
# This file includes the relevant testing commands required for 
# testing this directory and lists subdirectories to be tested as well.
add_test(_ctest_libmavconn_gtest_mavconn-test "/home/bjork/BurritoSwarm/flight_code/ROS/build/libmavconn/catkin_generated/env_cached.sh" "/usr/bin/python" "/opt/ros/jade/share/catkin/cmake/test/run_tests.py" "/home/bjork/BurritoSwarm/flight_code/ROS/build/libmavconn/test_results/libmavconn/gtest-mavconn-test.xml" "--return-code" "/home/bjork/BurritoSwarm/flight_code/ROS/devel/.private/libmavconn/lib/libmavconn/mavconn-test --gtest_output=xml:/home/bjork/BurritoSwarm/flight_code/ROS/build/libmavconn/test_results/libmavconn/gtest-mavconn-test.xml")
subdirs(gtest)
