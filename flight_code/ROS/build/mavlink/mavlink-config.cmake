if (mavlink_CONFIG_INCLUDED)
  return()
endif()
set(mavlink_CONFIG_INCLUDED TRUE)

set(mavlink_INCLUDE_DIRS "/home/bjork/BurritoSwarm/flight_code/ROS/devel/include")
set(mavlink_DIALECTS common;slugs;python_array_test;matrixpilot;minimal;ardupilotmega;paparazzi;autoquad;ASLUAV;ualberta;test)
set(mavlink2_DIALECTS common;slugs;python_array_test;matrixpilot;minimal;ardupilotmega;paparazzi;autoquad;ASLUAV;ualberta;test)

foreach(lib )
  set(onelib "${lib}-NOTFOUND")
  find_library(onelib ${lib}
      PATHS "/home/bjork/BurritoSwarm/flight_code/ROS/devel/lib"
    NO_DEFAULT_PATH
    )
  if(NOT onelib)
    message(FATAL_ERROR "Library '${lib}' in package mavlink is not installed properly")
  endif()
  list(APPEND mavlink_LIBRARIES ${onelib})
endforeach()

foreach(dep )
  if(NOT ${dep}_FOUND)
    find_package(${dep})
  endif()
  list(APPEND mavlink_INCLUDE_DIRS ${${dep}_INCLUDE_DIRS})
  list(APPEND mavlink_LIBRARIES ${${dep}_LIBRARIES})
endforeach()
