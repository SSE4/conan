set(CMAKE_SKIP_RPATH 1 CACHE BOOL "rpaths" FORCE)
# Policy CMP0068
# We want the old behavior, in CMake >= 3.9 CMAKE_SKIP_RPATH won't affect install_name in OSX
set(CMAKE_INSTALL_NAME_DIR "")
