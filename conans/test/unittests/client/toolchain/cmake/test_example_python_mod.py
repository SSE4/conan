from conans import CMakeToolchain
from conans.client.toolchain.cmake.os_host_mixins import AndroidHostMixin, oshost_mixins_registry
from conans.client.tools import chdir, load
from conans.test.unittests.client.toolchain.cmake.base_examples import ExamplesData
from conans.test.utils.mocks import ConanFileMock
from conans.test.utils.test_files import temp_folder


class ExampleCacheTemplatesTestCase(ExamplesData):
    """
    Another extension point could be to register python classes to the 'blocks' factory, note
    that the Conan canonical mechanism is still not decided
    """

    def test_override_mixin(self):
        # The user wants to _plugin_ some custom class (override/extend custom one)
        class CustomAndroidOSHostBlock(AndroidHostMixin):
            @property
            def android_ndk(self):
                return 'my/path/hardcoded'

        # Conan to provide a factory where we can register classes (context managed)
        old_oshost_mixins_registry = oshost_mixins_registry.copy()
        try:
            oshost_mixins_registry.update({'android': CustomAndroidOSHostBlock})

            conanfile = ConanFileMock()
            conanfile.settings = self.settings_android
            conanfile.settings_build = self.settings_macos

            # The user has some vendor toolchains:
            current_folder = temp_folder()
            with chdir(current_folder):
                tc = CMakeToolchain(conanfile)
                tc.write_toolchain_files()
                content = load(tc.get_filename())

            self.assertIn('my/path/hardcoded', content)
        finally:
            oshost_mixins_registry.update(old_oshost_mixins_registry)
