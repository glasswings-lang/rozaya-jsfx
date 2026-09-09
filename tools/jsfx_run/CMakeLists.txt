cmake_minimum_required(VERSION 3.16)
project(jsfx_run CXX)

# Point this at a ysfx checkout that has already been configured and built.
# See README.md in this directory for the exact commands.
set(YSFX_DIR "C:/git-src/ysfx" CACHE PATH "ysfx source directory")
set(YSFX_BUILD "${YSFX_DIR}/build" CACHE PATH "ysfx build directory")

add_executable(jsfx_run jsfx_run.cpp)
set_property(TARGET jsfx_run PROPERTY CXX_STANDARD 17)
target_include_directories(jsfx_run PRIVATE "${YSFX_DIR}/include")

target_link_libraries(jsfx_run PRIVATE
    "${YSFX_BUILD}/Release/ysfx.lib"
    "${YSFX_BUILD}/ysfx-private.dir/Release/ysfx-private.lib"
    "${YSFX_BUILD}/eel2.dir/Release/eel2.lib"
    "${YSFX_BUILD}/wdl-base.dir/Release/wdl-base.lib")

if(WIN32)
    target_link_libraries(jsfx_run PRIVATE winmm ole32 user32 gdi32 shell32 advapi32)
endif()
