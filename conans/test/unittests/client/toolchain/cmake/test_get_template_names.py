import unittest

from conans import Settings, ConanFile
from conans.client.conf import get_default_settings_yml
from conans.client.toolchain.cmake import CMakeToolchain
from conans.model.env_info import EnvValues
from conans.test.utils.mocks import TestBufferConanOutput


class GetTemplateNamesTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        settings = Settings.loads(get_default_settings_yml())
        settings.os = 'Windows'

        settings_build = Settings.loads(get_default_settings_yml())
        settings_build.os = 'Macos'

        cls.conanfile = ConanFile(TestBufferConanOutput(), None)
        cls.conanfile.initialize(Settings(), EnvValues())
        cls.conanfile.settings = settings
        cls.conanfile.settings_build = settings_build

    def test_unix_makefiles(self):
        self.conanfile.settings.os = 'Windows'
        self.conanfile.settings_build.os = 'Macos'

        tc = CMakeToolchain(self.conanfile, generator='Unix Makefiles')
        template_names = tc.get_template_names()
        self.assertListEqual(template_names, [
            'macos/toolchain_windows_unixmakefiles_apple-clang.cmake',
            'macos/toolchain_unixmakefiles_apple-clang.cmake',
            'macos/toolchain_windows_apple-clang.cmake',
            'macos/toolchain_apple-clang.cmake',
            'macos/toolchain_windows_unixmakefiles.cmake',
            'macos/toolchain_unixmakefiles.cmake',
            'macos/toolchain_windows.cmake',
            'macos/toolchain.cmake',
            'toolchain_windows_unixmakefiles_apple-clang.cmake',
            'toolchain_unixmakefiles_apple-clang.cmake',
            'toolchain_windows_apple-clang.cmake',
            'toolchain_apple-clang.cmake',
            'toolchain_windows_unixmakefiles.cmake',
            'toolchain_unixmakefiles.cmake',
            'toolchain_windows.cmake',
            'toolchain.cmake',
        ])

    def test_ios_xcode(self):
        self.conanfile.settings.os = 'iOS'
        self.conanfile.settings.compiler = 'apple-clang'
        self.conanfile.settings_build.os = 'Macos'

        tc = CMakeToolchain(self.conanfile, generator='Xcode')
        template_names = tc.get_template_names()
        self.assertListEqual(template_names, [
            'macos/toolchain_ios_xcode_apple-clang.cmake',
            'macos/toolchain_xcode_apple-clang.cmake',
            'macos/toolchain_ios_apple-clang.cmake',
            'macos/toolchain_apple-clang.cmake',
            'macos/toolchain_ios_xcode.cmake',
            'macos/toolchain_xcode.cmake',
            'macos/toolchain_ios.cmake',
            'macos/toolchain.cmake',
            'toolchain_ios_xcode_apple-clang.cmake',
            'toolchain_xcode_apple-clang.cmake',
            'toolchain_ios_apple-clang.cmake',
            'toolchain_apple-clang.cmake',
            'toolchain_ios_xcode.cmake',
            'toolchain_xcode.cmake',
            'toolchain_ios.cmake',
            'toolchain.cmake',
        ])
