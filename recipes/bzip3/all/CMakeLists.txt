cmake_minimum_required(VERSION 3.15)
project(bzip3 LANGUAGES C)

option(BZIP3_WITH_THREAD "enable thread" OFF)
option(BZIP3_WITH_UTIL "build and install utility" OFF)

set(BZIP3_INC
    ${BZIP3_SRC_DIR}/include/libbz3.h
)

add_library(bzip3)

if (BZIP3_VERSION VERSION_GREATER_EQUAL "1.1.5")
target_sources(bzip3 PRIVATE
    ${BZIP3_SRC_DIR}/src/libbz3.c
)
else()
target_sources(bzip3 PRIVATE
    ${BZIP3_SRC_DIR}/src/cm.c
    ${BZIP3_SRC_DIR}/src/crc32.c
    ${BZIP3_SRC_DIR}/src/libbz3.c
    ${BZIP3_SRC_DIR}/src/libsais.c
    ${BZIP3_SRC_DIR}/src/lzp.c
    ${BZIP3_SRC_DIR}/src/rle.c
)
endif()
target_include_directories(bzip3 PUBLIC ${BZIP3_SRC_DIR}/include)
set_target_properties(bzip3 PROPERTIES
    PUBLIC_HEADER "${BZIP3_INC}"
    C_VISIBILITY_PRESET hidden
    C_EXTENSIONS OFF
)
if (BZIP3_VERSION VERSION_GREATER_EQUAL "1.1.6" AND (MSVC OR MSVC90 OR MSVC10) AND BUILD_SHARED_LIBS)
    target_compile_definitions(bzip3 PRIVATE "BZIP3_DLL_EXPORT=1")
endif()

if (BZIP3_VERSION VERSION_GREATER_EQUAL "1.1.7")
    target_compile_definitions(bzip3 PRIVATE "VERSION=\"${BZIP3_VERSION}\"")
endif()

if (BZIP3_WITH_THREAD)
    find_package(Threads REQUIRED)
    target_link_libraries(bzip3 PRIVATE Threads::Threads)
    target_compile_definitions(bzip3 PRIVATE "PTHREAD")
endif()

if (BZIP3_WITH_UTIL)
    add_executable(bzip3_cmd ${BZIP3_SRC_DIR}/src/main.c)
    target_link_libraries(bzip3_cmd bzip3)
    target_compile_definitions(bzip3_cmd PRIVATE "VERSION=\"${BZIP3_VERSION}\"")
    set_target_properties(bzip3_cmd PROPERTIES OUTPUT_NAME "bzip3")
endif()

find_library(LIBM m)
target_link_libraries(bzip3 PRIVATE $<$<BOOL:${LIBM}>:${LIBM}>)

include(GNUInstallDirs)
install(
    TARGETS bzip3
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)

if (BZIP3_WITH_UTIL)
    install(TARGETS bzip3_cmd DESTINATION ${CMAKE_INSTALL_BINDIR})
endif()
