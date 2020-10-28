import os
import textwrap

from conans import CMakeToolchain
from conans.client.toolchain.cmake.os_host_mixins import oshost_mixins_registry, \
    UnixHostMixin
from conans.client.tools import chdir, load
from conans.paths import get_conan_user_home
from conans.test.unittests.client.toolchain.cmake.base_examples import ExamplesData
from conans.test.utils.mocks import ConanFileMock
from conans.test.utils.test_files import temp_folder
from conans.util.files import save


class ExampleExtendPythonNewTestCase(ExamplesData):
    """
    Another extension point could be to register python classes to the 'blocks' factory, note
    that the Conan canonical mechanism is still not decided
    """

    def test_add_new_compiler(self):
        # Conan has nothing built-in for Emscripten, but the user knows
        class EmscriptenOSHostBlock(UnixHostMixin):
            oshost_name = 'emscripten'
            oshost_blocks = ['blocks/oshost/emscripten.cmake']

            @property
            def crazy_value(self):
                return "Crazy-value-{}".format(self._conanfile.settings.os)

        # User provides the block too
        # We can override some blocks, maybe we want to HARDCODE something
        templates_folder = os.path.join(get_conan_user_home(), '.conan', 'templates')
        save(os.path.join(templates_folder, 'blocks', 'oshost', 'emscripten.cmake'),
             textwrap.dedent("""\
                # This is my EMSCRIPTEN block
                {{ tc.crazy_value }}
            """))

        # Conan to provide a factory where we can register classes (context managed)
        old_oshost_mixins_registry = oshost_mixins_registry.copy()
        try:
            oshost_mixins_registry.update({'emscripten': EmscriptenOSHostBlock})

            conanfile = ConanFileMock()
            conanfile.settings = self.settings_android
            conanfile.settings.os = 'Emscripten'
            conanfile.settings_build = self.settings_macos

            # The user has some vendor toolchains:
            current_folder = temp_folder()
            with chdir(current_folder):
                tc = CMakeToolchain(conanfile)
                tc.write_toolchain_files()
                content = load(tc.get_filename())

            self.assertIn('# This is my EMSCRIPTEN block', content)
            self.assertIn('Crazy-value-Emscripten', content)

        finally:
            oshost_mixins_registry.update(old_oshost_mixins_registry)
