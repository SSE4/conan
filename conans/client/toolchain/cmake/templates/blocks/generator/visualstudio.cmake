
set(CONAN_CXX_FLAGS "${CONAN_CXX_FLAGS} /MP{{ tc.cpu_count }}")
set(CONAN_C_FLAGS "${CONAN_C_FLAGS} /MP{{ tc.cpu_count }}")

set(CMAKE_GENERATOR_PLATFORM "{{ tc.generator_platform }}" CACHE STRING "" FORCE)
{% if tc.toolset %}set(CMAKE_GENERATOR_TOOLSET "{{ tc.toolset }}" CACHE STRING "" FORCE){% endif %}
