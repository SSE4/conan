{% if tc.architecture %}
set(CONAN_CXX_FLAGS "${CONAN_CXX_FLAGS} {{ tc.architecture }}")
set(CONAN_C_FLAGS "${CONAN_C_FLAGS} {{ tc.architecture }}")
set(CONAN_SHARED_LINKER_FLAGS "${CONAN_SHARED_LINKER_FLAGS} {{ tc.architecture }}")
set(CONAN_EXE_LINKER_FLAGS "${CONAN_EXE_LINKER_FLAGS} {{ tc.architecture }}")
{% endif %}
{% if tc.cppstd %}set(CMAKE_CXX_STANDARD {{ tc.cppstd }}){% endif %}
{% if tc.cppstd_extensions %}set(CMAKE_CXX_EXTENSIONS {{ tc.cppstd_extensions }}){% endif %}
{% if tc.libcxx %}set(CONAN_CXX_FLAGS "${CONAN_CXX_FLAGS} {{ tc.libcxx }}"){% endif %}
