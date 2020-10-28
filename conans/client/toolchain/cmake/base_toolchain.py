from conans.errors import ConanException


class BaseToolchain(object):
    generator_name = None
    oshost_name = None
    osbuild_name = None
    compiler_name = None
    oshost_blocks = []
    osbuild_blocks = []
    generator_blocks = []
    compiler_blocks = []

    def __init__(self, conanfile, **kwargs):
        self._conanfile = conanfile

        # To find the generated cmake_find_package finders
        self.cmake_prefix_path = "${CMAKE_BINARY_DIR}"
        self.cmake_module_path = "${CMAKE_BINARY_DIR}"

    def get_compiler_features_blocks(self):
        return self.osbuild_blocks + self.oshost_blocks + self.generator_blocks + self.compiler_blocks

    def get_project_config_blocks(self):
        return []

    @property
    def build_type(self):
        return self._conanfile.settings.build_type

    @property
    def shared_libs(self):
        try:
            return "ON" if self._conanfile.options.shared else "OFF"
        except ConanException:
            return None
