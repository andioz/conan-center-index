cmake_minimum_required(VERSION 3.15)
project(test_package)

find_package(range-v3 REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} range-v3::range-v3)
if(MSVC AND range-v3_VERSION STREQUAL "0.10.0")
  set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 20)
else()
  set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 17)
endif()
