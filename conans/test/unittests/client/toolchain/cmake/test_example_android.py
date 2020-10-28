import textwrap

from conans import CMakeToolchain
from conans.client.tools import chdir, load
from conans.test.unittests.client.toolchain.cmake.base_examples import ExamplesData
from conans.test.utils.mocks import ConanFileMock
from conans.test.utils.test_files import temp_folder


class ExampleAndroidTestCase(ExamplesData):
    """
    Conan composes the template taking into account given configuration
    """

    def test_android(self):
        conanfile = ConanFileMock()
        conanfile.settings = self.settings_android
        conanfile.settings_build = self.settings_macos

        tc = CMakeToolchain(conanfile)
        tc.variables.debug["MYVAR"] = "DEBUG_VALUE"
        tc.variables.release["MYVAR"] = "RELEASE_VALUE"

        current_folder = temp_folder()
        with chdir(current_folder):
            tc.write_toolchain_files()
            content = load(tc.get_filename())

        self.assertListEqual(content.splitlines(), textwrap.dedent("""
            # Conan automatically generated toolchain file
            # DO NOT EDIT MANUALLY, it will be overwritten

            # Avoid including toolchain file several times (bad if appending to variables like
            #   CMAKE_CXX_FLAGS. See https://github.com/android/ndk/issues/323
            if(CONAN_TOOLCHAIN_INCLUDED)
              return()
            endif()
            set(CONAN_TOOLCHAIN_INCLUDED TRUE)

            # Include 'blocks/osbuild/crossbuild.cmake'
            set(CMAKE_SYSTEM_NAME Android)

            # Include 'blocks/oshost/unix.cmake'
            set(CMAKE_SYSTEM_VERSION 23)

            # Include 'blocks/oshost/android.cmake'
            set(CMAKE_ANDROID_ARCH_ABI x86_64)
            set(CMAKE_ANDROID_STL_TYPE c++_shared)
            set(CMAKE_ANDROID_NDK /Users/jgsogo/Library/Android/sdk/ndk/21.0.6113669)

            # Include 'blocks/compiler/compiler.cmake'

            set(CONAN_CXX_FLAGS "${CONAN_CXX_FLAGS} -m64")
            set(CONAN_C_FLAGS "${CONAN_C_FLAGS} -m64")
            set(CONAN_SHARED_LINKER_FLAGS "${CONAN_SHARED_LINKER_FLAGS} -m64")
            set(CONAN_EXE_LINKER_FLAGS "${CONAN_EXE_LINKER_FLAGS} -m64")

            get_property( _CMAKE_IN_TRY_COMPILE GLOBAL PROPERTY IN_TRY_COMPILE )
            if(_CMAKE_IN_TRY_COMPILE)
                message(STATUS "Running toolchain IN_TRY_COMPILE")
                return()
            endif()

            set(CMAKE_EXPORT_NO_PACKAGE_REGISTRY ON)

            # To support the cmake_find_package generators
            set(CMAKE_MODULE_PATH ${CMAKE_BINARY_DIR} ${CMAKE_MODULE_PATH})
            set(CMAKE_PREFIX_PATH ${CMAKE_BINARY_DIR} ${CMAKE_PREFIX_PATH})

            set(CMAKE_BUILD_TYPE "Release" CACHE STRING "Choose the type of build." FORCE)

            set(CONAN_CXX_FLAGS "${CONAN_CXX_FLAGS} -m64")
            set(CONAN_C_FLAGS "${CONAN_C_FLAGS} -m64")
            set(CONAN_SHARED_LINKER_FLAGS "${CONAN_SHARED_LINKER_FLAGS} -m64")
            set(CONAN_EXE_LINKER_FLAGS "${CONAN_EXE_LINKER_FLAGS} -m64")

            set(CMAKE_CXX_FLAGS_INIT "${CONAN_CXX_FLAGS}" CACHE STRING "" FORCE)
            set(CMAKE_C_FLAGS_INIT "${CONAN_C_FLAGS}" CACHE STRING "" FORCE)
            set(CMAKE_SHARED_LINKER_FLAGS_INIT "${CONAN_SHARED_LINKER_FLAGS}" CACHE STRING "" FORCE)
            set(CMAKE_EXE_LINKER_FLAGS_INIT "${CONAN_EXE_LINKER_FLAGS}" CACHE STRING "" FORCE)

            # Variables

            # Variables per configuration

            set(MYVAR $<IF:$<CONFIG:debug>,"DEBUG_VALUE",$<IF:$<CONFIG:release>,"RELEASE_VALUE","">>)

            # Preprocessor definitions

            # Preprocessor definitions per configuration

         """).splitlines())
