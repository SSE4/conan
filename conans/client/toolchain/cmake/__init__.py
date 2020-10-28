import os
from collections import defaultdict

from jinja2 import Environment, select_autoescape, FileSystemLoader, ChoiceLoader

from conans.client.build.cmake_flags import get_generator
from conans.client.tools import OrderedDict, cross_building
from conans.paths import get_conan_user_home
from conans.util.files import save, load
from .base_toolchain import BaseToolchain
from .generators_mixins import get_mixin as get_generator_mixin
from .os_build_mixins import get_mixin as get_os_build_mixin
from .os_host_mixins import get_mixin as get_os_host_mixin
from .compiler_mixins import get_mixin as get_compiler_mixin
import re

class CMakeToolchain(object):
    template_name = None
    template_file = None
    filename = None

    def __init__(self, conanfile, generator=None, **kwargs):
        self._get_parts_names(conanfile, generator)
        self.variables = Variables()
        self.preprocessor_definitions = Variables()

        ToolchainClass = self._get_toolchain_class()
        self._toolchain = ToolchainClass(conanfile, **kwargs)

    def _get_parts_names(self, conanfile, generator):
        self.oshost_name = str(conanfile.settings.os).replace(' ', '').lower()
        self.osbuild_name = str(conanfile.settings_build.os).replace(' ', '').lower()
        self.compiler_name = str(conanfile.settings.compiler).replace(' ', '').lower()
        self.xbuild = cross_building(conanfile, skip_x64_x86=True)
        generator = generator or get_generator(conanfile=conanfile)
        self.generator_name = generator.replace(' ', '').lower()

    def _get_toolchain_class(self):
        base_mixins = [get_os_build_mixin(self.osbuild_name, xbuilding=self.xbuild),
                       get_os_host_mixin(self.oshost_name),
                       get_generator_mixin(self.generator_name),
                       get_compiler_mixin(self.compiler_name),
                       BaseToolchain]
        return type('ToolchainClass', tuple(base_mixins), {})

    def get_template_names(self):
        if self.template_name:
            return [self.template_name, ]
        else:
            template_names = ['toolchain']

            append = ['{}_{}'.format(it, self.oshost_name) for it in template_names]
            template_names += append

            append = ['{}_{}'.format(it, self.generator_name) for it in template_names]
            template_names += append

            append = ['{}_{}'.format(it, self.compiler_name) for it in template_names]
            template_names += append

            append = ['{}/{}'.format(self.osbuild_name, it) for it in template_names]
            template_names += append

            template_names = ['{}.cmake'.format(it) for it in reversed(template_names)]
            return template_names

    def get_filename(self):
        if self.filename:
            return self.filename
        else:
            # It adds only the pieces that contribute to modify the content: host and generator
            filename = 'toolchain'
            if self._toolchain.oshost_name:
                filename += '_{}'.format(self._toolchain.oshost_name)
            if self._toolchain.generator_name:
                filename += '_{}'.format(self._toolchain.generator_name)
            return filename + '.cmake'

    def write_toolchain_files(self):
        template_names = self.get_template_names()
        filename = self.get_filename()
        context = {
            'tc': self._toolchain,
            'variables': self.variables,
            'preprocessor_definitions': self.preprocessor_definitions
        }
        # TODO: Use the 'get_templates' from the Cache class
        cache_folder = os.path.join(get_conan_user_home(), '.conan')
        loaders = [FileSystemLoader(os.path.join(cache_folder, 'templates')),
                   FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),]
        env = Environment(loader=ChoiceLoader(loaders),
                          autoescape=select_autoescape(['html', 'xml']))
        if self.template_file:
            tpl = env.from_string(load(self.template_file))
        else:
            tpl = env.select_template(template_names)
        content = tpl.render(**context)
        content = re.sub(r'(\s*\r?\n){3,}', '\r\n\r\n', content)
        save(filename, content)


class Variables(OrderedDict):
    _configuration_types = None  # Needed for py27 to avoid infinite recursion

    def __init__(self):
        super(Variables, self).__init__()
        self._configuration_types = {}

    def __getattribute__(self, config):
        try:
            return super(Variables, self).__getattribute__(config)
        except AttributeError:
            return self._configuration_types.setdefault(config, dict())

    @property
    def configuration_types(self):
        # Reverse index for the configuration_types variables
        ret = defaultdict(list)
        for conf, definitions in self._configuration_types.items():
            for k, v in definitions.items():
                ret[k].append((conf, v))
        return ret
