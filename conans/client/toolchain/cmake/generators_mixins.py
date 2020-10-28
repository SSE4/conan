from conans.client.tools import cpu_count


class GeneratorMixin(object):
    _conanfile = None


class NinjaMixin(GeneratorMixin):
    generator_name = 'ninja'


class VisualStudioMixin(GeneratorMixin):
    generator_name = 'visualstudio'
    generator_blocks = ['blocks/generator/visualstudio.cmake']

    @property
    def cpu_count(self):
        return cpu_count(output=self._conanfile.output)

    @property
    def generator_platform(self):
        arch = self._conanfile.settings.arch
        return {"x86": "Win32",
                "x86_64": "x64",
                "armv7": "ARM",
                "armv8": "ARM64"}.get(arch)

    @property
    def toolset(self):
        return self._conanfile.settings.compiler.toolset


def get_mixin(generator_name):
    # TODO: If we really want to let the user inject behaviour into our hierarchy of classes,
    #   then we can turn this into a factory and allow registration from outside
    if generator_name == NinjaMixin.generator_name:
        return NinjaMixin
    elif generator_name.startswith(VisualStudioMixin.generator_name):
        return VisualStudioMixin
    else:
        return GeneratorMixin
