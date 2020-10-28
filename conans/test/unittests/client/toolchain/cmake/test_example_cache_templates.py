import os
import textwrap

from conans import CMakeToolchain
from conans.client.tools import chdir, load, save
from conans.paths import get_conan_user_home
from conans.test.unittests.client.toolchain.cmake.base_examples import ExamplesData
from conans.test.utils.mocks import ConanFileMock
from conans.test.utils.test_files import temp_folder


class ExampleCacheTemplatesTestCase(ExamplesData):
    """
    The user can override built-in templates with its own ones by adding files to the cache,
    these overrides will affect every rendered template.
    """

    def test_base_template_override(self):
        # We can override the base template: toolchain.cmake
        templates_folder = os.path.join(get_conan_user_home(), '.conan', 'templates')
        save(os.path.join(templates_folder, 'toolchain.cmake'), textwrap.dedent("""
            # MY COMPANY BASE TEMPLATE
        """))

        conanfile = ConanFileMock()
        conanfile.settings = self.settings_macos
        conanfile.settings_build = self.settings_macos

        # The user has some vendor toolchains:
        current_folder = temp_folder()
        with chdir(current_folder):
            tc = CMakeToolchain(conanfile)
            tc.write_toolchain_files()
            content = load(tc.get_filename())

        self.assertListEqual(content.splitlines(), textwrap.dedent("""
            # MY COMPANY BASE TEMPLATE
         """).splitlines())

    def test_specific_template_override(self):
        # We can override the template only for some configurations, and it will affect only
        #   those configurations
        templates_folder = os.path.join(get_conan_user_home(), '.conan', 'templates')
        save(os.path.join(templates_folder, 'toolchain_macos_unixmakefiles.cmake'),
             textwrap.dedent("""
                # MY COMPANY BASE TEMPLATE --- Unix templates
            """))

        conanfile = ConanFileMock()
        conanfile.settings = self.settings_macos
        conanfile.settings_build = self.settings_macos

        # The user has some vendor toolchains:
        current_folder = temp_folder()
        with chdir(current_folder):
            tc = CMakeToolchain(conanfile)
            tc.write_toolchain_files()
            content = load(tc.get_filename())

        self.assertListEqual(content.splitlines(), textwrap.dedent("""
            # MY COMPANY BASE TEMPLATE --- Unix templates
         """).splitlines())

        # Other configurations are not affected
        conanfile.settings = self.settings_linux
        with chdir(current_folder):
            tc = CMakeToolchain(conanfile)
            tc.write_toolchain_files()
            content = load(tc.get_filename())

        self.assertNotIn('# MY COMPANY BASE TEMPLATE', content)

    def test_single_block_override(self):
        # We can override some blocks, maybe we want to HARDCODE something
        templates_folder = os.path.join(get_conan_user_home(), '.conan', 'templates')
        save(os.path.join(templates_folder, 'blocks', 'oshost', 'android.cmake'), textwrap.dedent("""
            set(CMAKE_ANDROID_ARCH_ABI {{ tc.android_arch_abi }})
            set(CMAKE_ANDROID_STL_TYPE {{ tc.android_stl_type }})
            set(CMAKE_ANDROID_NDK "/this/is/my/hardcoded/path")
        """))

        conanfile = ConanFileMock()
        conanfile.settings = self.settings_android
        conanfile.settings_build = self.settings_macos

        # The user has some vendor toolchains:
        current_folder = temp_folder()
        with chdir(current_folder):
            tc = CMakeToolchain(conanfile)
            tc.write_toolchain_files()
            content = load(tc.get_filename())

        self.assertIn('set(CMAKE_ANDROID_NDK "/this/is/my/hardcoded/path")', content)
