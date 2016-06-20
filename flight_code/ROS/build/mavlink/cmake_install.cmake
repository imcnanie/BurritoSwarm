# Install script for directory: /home/bjork/BurritoSwarm/flight_code/ROS/src/mavlink

# Set the install prefix
if(NOT DEFINED CMAKE_INSTALL_PREFIX)
  set(CMAKE_INSTALL_PREFIX "/home/bjork/BurritoSwarm/flight_code/ROS/devel")
endif()
string(REGEX REPLACE "/$" "" CMAKE_INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}")

# Set the install configuration name.
if(NOT DEFINED CMAKE_INSTALL_CONFIG_NAME)
  if(BUILD_TYPE)
    string(REGEX REPLACE "^[^A-Za-z0-9_]+" ""
           CMAKE_INSTALL_CONFIG_NAME "${BUILD_TYPE}")
  else()
    set(CMAKE_INSTALL_CONFIG_NAME "")
  endif()
  message(STATUS "Install configuration: \"${CMAKE_INSTALL_CONFIG_NAME}\"")
endif()

# Set the component getting installed.
if(NOT CMAKE_INSTALL_COMPONENT)
  if(COMPONENT)
    message(STATUS "Install component: \"${COMPONENT}\"")
    set(CMAKE_INSTALL_COMPONENT "${COMPONENT}")
  else()
    set(CMAKE_INSTALL_COMPONENT)
  endif()
endif()

# Install shared libraries without execute permission?
if(NOT DEFINED CMAKE_INSTALL_SO_NO_EXE)
  set(CMAKE_INSTALL_SO_NO_EXE "1")
endif()

if(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "Dev")
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/mavlink" TYPE FILE FILES "/home/bjork/BurritoSwarm/flight_code/ROS/build/mavlink/config.h")
endif()

if(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "Dev")
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/mavlink" TYPE DIRECTORY FILES "/home/bjork/BurritoSwarm/flight_code/ROS/build/mavlink/include/" FILES_MATCHING REGEX "/[^/]*\\.h[^/]*$")
endif()

if(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "Dev")
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/mavlink" TYPE DIRECTORY FILES "/home/bjork/BurritoSwarm/flight_code/ROS/build/mavlink/src/" FILES_MATCHING REGEX "/[^/]*\\.c[^/]*$")
endif()

if(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "Dev")
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share" TYPE DIRECTORY FILES "/home/bjork/BurritoSwarm/flight_code/ROS/src/mavlink/share/mavlink" FILES_MATCHING REGEX "/[^/]*\\.c[^/]*$")
endif()

if(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "cmake")
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/mavlink/cmake" TYPE FILE FILES "/home/bjork/BurritoSwarm/flight_code/ROS/build/mavlink/mavlink-config.cmake")
endif()

if(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "pkgconfig")
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/pkgconfig" TYPE FILE FILES "/home/bjork/BurritoSwarm/flight_code/ROS/build/mavlink/mavlink.pc")
endif()

if(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "license")
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/mavlink" TYPE FILE FILES "/home/bjork/BurritoSwarm/flight_code/ROS/build/mavlink/COPYING.txt")
endif()

if(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "catkin")
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/mavlink" TYPE FILE FILES "/home/bjork/BurritoSwarm/flight_code/ROS/src/mavlink/package.xml")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for each subdirectory.
  include("/home/bjork/BurritoSwarm/flight_code/ROS/build/mavlink/pymavlink/cmake_install.cmake")

endif()

if(CMAKE_INSTALL_COMPONENT)
  set(CMAKE_INSTALL_MANIFEST "install_manifest_${CMAKE_INSTALL_COMPONENT}.txt")
else()
  set(CMAKE_INSTALL_MANIFEST "install_manifest.txt")
endif()

string(REPLACE ";" "\n" CMAKE_INSTALL_MANIFEST_CONTENT
       "${CMAKE_INSTALL_MANIFEST_FILES}")
file(WRITE "/home/bjork/BurritoSwarm/flight_code/ROS/build/mavlink/${CMAKE_INSTALL_MANIFEST}"
     "${CMAKE_INSTALL_MANIFEST_CONTENT}")
