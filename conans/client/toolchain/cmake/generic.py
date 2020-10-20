import os
import textwrap

from conans.client.build.cmake_flags import get_generator, get_generator_platform, get_toolset, \
    is_multi_configuration
from conans.client.build.compiler_flags import architecture_flag
from conans.client.tools import cpu_count, load
from conans.errors import ConanException
from .base import CMakeToolchainBase


# https://stackoverflow.com/questions/30503631/cmake-in-which-order-are-files-parsed-cache-toolchain-etc
# https://cmake.org/cmake/help/v3.6/manual/cmake-toolchains.7.html
# https://github.com/microsoft/vcpkg/tree/master/scripts/buildsystems


class CMakeGenericToolchain(CMakeToolchainBase):

    _template_project_include = textwrap.dedent("""
        # When using a Conan toolchain, this file is included as the last step of `project()` calls.
        #  https://cmake.org/cmake/help/latest/variable/CMAKE_PROJECT_INCLUDE.html

        if (NOT CONAN_TOOLCHAIN_INCLUDED)
            message(FATAL_ERROR "This file is expected to be used together with the Conan toolchain")
        endif()

        ########### Utility macros and functions ###########
        function(conan_get_policy policy_id policy)
            if(POLICY "${policy_id}")
                cmake_policy(GET "${policy_id}" _policy)
                set(${policy} "${_policy}" PARENT_SCOPE)
            else()
                set(${policy} "" PARENT_SCOPE)
            endif()
        endfunction()
        ########### End of Utility macros and functions ###########

        # Adjustments that depends on the build_type
        {% if vs_static_runtime %}
        conan_get_policy(CMP0091 policy_0091)
        if(policy_0091 STREQUAL "NEW")
            set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")
        else()
            foreach(flag CMAKE_C_FLAGS_RELEASE CMAKE_CXX_FLAGS_RELEASE
                         CMAKE_C_FLAGS_RELWITHDEBINFO CMAKE_CXX_FLAGS_RELWITHDEBINFO
                         CMAKE_C_FLAGS_MINSIZEREL CMAKE_CXX_FLAGS_MINSIZEREL
                         CMAKE_C_FLAGS_DEBUG CMAKE_CXX_FLAGS_DEBUG)
                if(DEFINED ${flag})
                    string(REPLACE "/MD" "/MT" ${flag} "${${flag}}")
                endif()
            endforeach()
        endif()
        {% endif %}
    """)

    def __init__(self, conanfile, generator=None, generator_platform=None, build_type=None,
                 toolset=None, parallel=True):
        super(CMakeGenericToolchain, self).__init__(conanfile)

        the_os = conanfile.settings.get_safe("os")
        toolchain_name = "%s.toolchain.cmake.tmpl" % the_os.lower()
        if not os.path.isfile(os.path.join(self._template_folder, toolchain_name)):
            toolchain_name = "generic.toolchain.cmake.tmpl"
        if the_os == "Android":
            # FIXME: don't like it here, does it belong to the toolchain itself?
            # FIXME: how do we propagate path to the NDK? Emscripten would be a similar story
            android_ndk = '/Users/sse4/Android/android-ndk-r21d'
            self.base_toolchain = os.path.join(android_ndk, "build", "cmake",
                                               "android.toolchain.cmake")
        self._template_toolchain = load(os.path.join(self._template_folder, toolchain_name))

        self.fpic = self._deduce_fpic()
        self.vs_static_runtime = self._deduce_vs_static_runtime()
        self.parallel = parallel

        # To find the generated cmake_find_package finders
        self.cmake_prefix_path = "${CMAKE_BINARY_DIR}"
        self.cmake_module_path = "${CMAKE_BINARY_DIR}"

        self.generator = generator or get_generator(self._conanfile)
        self.generator_platform = (generator_platform or
                                   get_generator_platform(self._conanfile.settings,
                                                          self.generator))
        self.toolset = toolset or get_toolset(self._conanfile.settings, self.generator)

        try:
            self._build_shared_libs = "ON" if self._conanfile.options.shared else "OFF"
        except ConanException:
            self._build_shared_libs = None

        self.set_libcxx, self.glibcxx = self._get_libcxx()

        self.parallel = None
        if parallel:
            if self.generator and "Visual Studio" in self.generator:
                self.parallel = "/MP%s" % cpu_count(output=self._conanfile.output)

        self.cppstd, self.cppstd_extensions = self._cppstd()

        self.skip_rpath = True if self._conanfile.settings.get_safe("os") == "Macos" else False
        self.architecture = self._get_architecture()

        # TODO: I would want to have here the path to the compiler too
        build_type = build_type or self._conanfile.settings.get_safe("build_type")
        self.build_type = build_type if not is_multi_configuration(self.generator) else None

    def _deduce_fpic(self):
        fpic = self._conanfile.options.get_safe("fPIC")
        if fpic is None:
            return None
        os_ = self._conanfile.settings.get_safe("os")
        if os_ and "Windows" in os_:
            self._conanfile.output.warn("Toolchain: Ignoring fPIC option defined for Windows")
            return None
        shared = self._conanfile.options.get_safe("shared")
        if shared:
            self._conanfile.output.warn("Toolchain: Ignoring fPIC option defined "
                                        "for a shared library")
            return None
        return fpic

    def _get_architecture(self):
        # This should be factorized and make it toolchain-private
        return architecture_flag(self._conanfile.settings)

    def _deduce_vs_static_runtime(self):
        settings = self._conanfile.settings
        if (settings.get_safe("compiler") == "Visual Studio" and
            "MT" in settings.get_safe("compiler.runtime")):
            return True
        return False

    def _get_libcxx(self):
        libcxx = self._conanfile.settings.get_safe("compiler.libcxx")
        if not libcxx:
            return None, None
        compiler = self._conanfile.settings.compiler
        lib = glib = None
        if compiler == "apple-clang":
            # In apple-clang 2 only values atm are "libc++" and "libstdc++"
            lib = "-stdlib={}".format(libcxx)
        elif compiler == "clang":
            if libcxx == "libc++":
                lib = "-stdlib=libc++"
            elif libcxx == "libstdc++" or libcxx == "libstdc++11":
                lib = "-stdlib=libstdc++"
            # FIXME, something to do with the other values? Android c++_shared?
        elif compiler == "sun-cc":
            lib = {"libCstd": "Cstd",
                   "libstdcxx": "stdcxx4",
                   "libstlport": "stlport4",
                   "libstdc++": "stdcpp"
                   }.get(libcxx)
            if lib:
                lib = "-library={}".format(lib)
        elif compiler == "gcc":
            if libcxx == "libstdc++11":
                glib = "1"
            elif libcxx == "libstdc++":
                glib = "0"
        return lib, glib

    def _cppstd(self):
        cppstd = cppstd_extensions = None
        compiler_cppstd = self._conanfile.settings.get_safe("compiler.cppstd")
        if compiler_cppstd:
            if compiler_cppstd.startswith("gnu"):
                cppstd = compiler_cppstd[3:]
                cppstd_extensions = "ON"
            else:
                cppstd = compiler_cppstd
                cppstd_extensions = "OFF"
        return cppstd, cppstd_extensions

    def _get_template_context_data(self):
        ctxt_toolchain, ctxt_project_include = \
            super(CMakeGenericToolchain, self)._get_template_context_data()
        ctxt_toolchain.update({
            "build_type": self.build_type,
            "generator_platform": self.generator_platform,
            "toolset": self.toolset,
            "cmake_prefix_path": self.cmake_prefix_path,
            "cmake_module_path": self.cmake_module_path,
            "fpic": self.fpic,
            "skip_rpath": self.skip_rpath,
            "set_libcxx": self.set_libcxx,
            "glibcxx": self.glibcxx,
            "parallel": self.parallel,
            "cppstd": self.cppstd,
            "cppstd_extensions": self.cppstd_extensions,
            "shared_libs": self._build_shared_libs,
            "architecture": self.architecture
        })
        ctxt_project_include.update({'vs_static_runtime': self.vs_static_runtime})
        return ctxt_toolchain, ctxt_project_include
