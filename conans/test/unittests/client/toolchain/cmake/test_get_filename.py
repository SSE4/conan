import unittest

from conans import Settings, ConanFile
from conans.client.conf import get_default_settings_yml
from conans.client.toolchain.cmake import CMakeToolchain
from conans.model.env_info import EnvValues
from conans.test.utils.mocks import TestBufferConanOutput


class GetFilenameTestCase(unittest.TestCase):

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

    def test_host_value(self):
        self.conanfile.settings.os = 'Windows'
        self.assertEquals('toolchain.cmake', CMakeToolchain(self.conanfile).get_filename())

        self.conanfile.settings.os = 'Macos'
        self.assertEquals('toolchain_unix.cmake', CMakeToolchain(self.conanfile).get_filename())

        self.conanfile.settings.os = 'Linux'
        self.assertEquals('toolchain_unix.cmake', CMakeToolchain(self.conanfile).get_filename())

        self.conanfile.settings.os = 'Android'
        self.assertEquals('toolchain_android.cmake', CMakeToolchain(self.conanfile).get_filename())
