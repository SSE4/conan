{# It is ok to modify content here, these are options of the project itself. There is no alternative #}
{%- if tc.fpic %}set(CMAKE_POSITION_INDEPENDENT_CODE ON){% endif %}
{%- if tc.cmake_system_version %}set(CMAKE_SYSTEM_VERSION {{ tc.cmake_system_version }}){% endif %}
