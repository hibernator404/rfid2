cmake_minimum_required(VERSION 3.25)
project(clionproject)

set(CMAKE_CXX_STANDARD 14)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++14 -lcurl")

# 设置curl库的路径
set(CURL_LIBRARY_DIRS D:/soft_enviorment/crul/curl-8.8.0_2-win64-mingw/lib)
set(CURL_INCLUDE_DIRS D:/soft_enviorment/crul/curl-8.8.0_2-win64-mingw/include)

# 添加curl库
include_directories(${CURL_INCLUDE_DIRS})
link_directories(${CURL_LIBRARY_DIRS})

add_executable(clionproject main.cpp SerialPort.cpp stdafx.cpp)

target_link_libraries(clionproject curl)
