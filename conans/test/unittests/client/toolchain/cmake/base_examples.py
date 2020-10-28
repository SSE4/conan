from conans import Settings
from conans.client.conf import get_default_settings_yml
import unittest

from conans.client.tools import environment_append
from conans.test.utils.test_files import temp_folder


class ExamplesData(unittest.TestCase):
    maxDiff = None

    def run(self, *args, **kwargs):
        current_folder = temp_folder()
        with environment_append({'CONAN_USER_HOME': current_folder}):
            super(ExamplesData, self).run(*args, **kwargs)

    @property
    def settings_macos(self):
        settings = Settings.loads(get_default_settings_yml())
        settings.os = 'Macos'
        settings.arch = 'x86_64'
        settings.compiler = 'apple-clang'
        settings.compiler.version = '11.0'
        settings.compiler.libcxx = 'libc++'
        settings.build_type = 'Release'
        return settings

    @property
    def settings_linux(self):
        settings = Settings.loads(get_default_settings_yml())
        settings.os = 'Linux'
        settings.arch = 'x86_64'
        settings.compiler = 'gcc'
        settings.compiler.version = '9'
        settings.compiler.libcxx = 'libstdc++11'
        settings.build_type = 'Release'
        return settings

    @property
    def settings_android(self):
        settings = Settings.loads(get_default_settings_yml())
        settings.os = 'Android'
        settings.os.api_level = '23'
        settings.arch = 'x86_64'
        settings.compiler = 'clang'
        settings.compiler.version = '9'
        settings.compiler.libcxx = 'c++_shared'
        settings.build_type = 'Release'
        return settings

