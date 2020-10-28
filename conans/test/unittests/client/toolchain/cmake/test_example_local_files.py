import textwrap

from conans import CMakeToolchain
from conans.client.tools import chdir, load, save
from conans.test.unittests.client.toolchain.cmake.base_examples import ExamplesData
from conans.test.utils.mocks import ConanFileMock
from conans.test.utils.test_files import temp_folder


class ExampleVendorToolchainTestCase(ExamplesData):
    """
    The user can provide files (or templates) located in a given directory
    """

    def test_local_file(self):
        conanfile = ConanFileMock()
        conanfile.settings = self.settings_macos
        conanfile.settings_build = self.settings_macos

        # The user has some vendor toolchains:
        current_folder = temp_folder()
        with chdir(current_folder):
            save('vendor_toolchain.cmake', textwrap.dedent("""
                # This is my vendor toolchain, it contains everything I need
            """))

            tc = CMakeToolchain(conanfile)
            tc.template_file = 'vendor_toolchain.cmake'
            tc.write_toolchain_files()
            content = load(tc.get_filename())

        self.assertListEqual(content.splitlines(), textwrap.dedent("""
            # This is my vendor toolchain, it contains everything I need
         """).splitlines())

    def test_local_template(self):
        conanfile = ConanFileMock()
        conanfile.settings = self.settings_macos
        conanfile.settings_build = self.settings_macos

        # The user has some vendor toolchains:
        current_folder = temp_folder()
        with chdir(current_folder):
            save('vendor_toolchain.cmake', textwrap.dedent("""
                # This is my vendor toolchain, it almost contains everything I need
                set(BUILD_TYPE {{ tc.build_type }})
            """))

            tc = CMakeToolchain(conanfile)
            tc.template_file = 'vendor_toolchain.cmake'
            tc.write_toolchain_files()
            content = load(tc.get_filename())

        self.assertListEqual(content.splitlines(), textwrap.dedent("""
            # This is my vendor toolchain, it almost contains everything I need
            set(BUILD_TYPE Release)
         """).splitlines())
