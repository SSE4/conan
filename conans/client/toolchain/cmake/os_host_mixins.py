class OSHostDefaultMixin(object):
    _conanfile = None
    generator_name = None


class UnixHostMixin(OSHostDefaultMixin):
    oshost_name = 'unix'
    oshost_blocks = ['blocks/oshost/unix.cmake']

    @property
    def fpic(self):
        shared = self._conanfile.options.get_safe("shared")
        if shared:
            self._conanfile.output.warn("Toolchain: Ignoring fPIC option defined "
                                        "for a shared library")
            return None
        return self._conanfile.options.get_safe("fPIC")

    @property
    def cmake_system_version(self):
        return self._conanfile.settings.get_safe('os.version')


class MacosMixin(UnixHostMixin):
    oshost_name = 'macos'
    oshost_blocks = UnixHostMixin.oshost_blocks + ['blocks/oshost/macos.cmake']


class AndroidHostMixin(UnixHostMixin):
    oshost_name = 'android'
    oshost_blocks = UnixHostMixin.oshost_blocks + ['blocks/oshost/android.cmake']

    @property
    def cmake_system_version(self):
        return self._conanfile.settings.os.api_level

    @property
    def android_arch_abi(self):
        return {"x86": "x86",
                "x86_64": "x86_64",
                "armv7": "armeabi-v7a",
                "armv8": "arm64-v8a"}.get(str(self._conanfile.settings.arch))

    @property
    def android_stl_type(self):
        libcxx_str = str(self._conanfile.settings.compiler.libcxx)
        return libcxx_str  # TODO: only 'c++_shared' y 'c++_static' supported?

    @property
    def android_ndk(self):
        return '/Users/jgsogo/Library/Android/sdk/ndk/21.0.6113669'  # TODO: ???


class WindowsCEMixin(OSHostDefaultMixin):
    oshost_name = 'windowsce'

    @property
    def generator_platform(self):
        assert self.generator_name == 'visualstudio', "Got '{}'!".format(self.generator_name)
        return self._conanfile.settings.get_safe("os.platform")


# TODO: Just for demo purposes, choose a factory pattern implementation!
oshost_mixins_registry = {
    AndroidHostMixin.oshost_name: AndroidHostMixin,
    'linux': UnixHostMixin,
    'macos': UnixHostMixin,
    'windowsce': WindowsCEMixin,
}


def get_mixin(oshost_name):
    # TODO: If we really want to let the user inject behaviour into our hierarchy of classes,
    #   then we can turn this into a factory and allow registration from outside
    return oshost_mixins_registry.get(oshost_name, OSHostDefaultMixin)
