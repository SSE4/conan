class CompilerMixin(object):
    _conanfile = None
    compiler_blocks = ['blocks/compiler/compiler.cmake', ]

    @property
    def cppstd(self):
        compiler_cppstd = self._conanfile.settings.get_safe("compiler.cppstd")
        if compiler_cppstd:
            cppstd = compiler_cppstd[3:] if compiler_cppstd.startswith("gnu") else compiler_cppstd
            return cppstd
        return None

    @property
    def cppstd_extensions(self):
        compiler_cppstd = self._conanfile.settings.get_safe("compiler.cppstd")
        if compiler_cppstd:
            return "ON" if compiler_cppstd.startswith("gnu") else "OFF"
        return None

    @property
    def libcxx(self):
        return None

    @property
    def architecture(self):
        return None


class IntelCompilerMixin(CompilerMixin):
    compiler_name = 'intel'

    @property
    def architecture(self):
        arch = self._conanfile.settings.get_safe("arch")
        compiler_base = self._conanfile.settings.get_safe("compiler.base")
        if str(arch) == "x86":
            return "/Qm32" if str(compiler_base) == "Visual Studio" else "-m32"
        elif str(arch) == "x86_64":
            return "/Qm64" if str(compiler_base) == "Visual Studio" else "-m64"
        return None


class UnixCompilerMixin(CompilerMixin):
    @property
    def architecture(self):
        arch = self._conanfile.settings.get_safe("arch")
        the_os = self._conanfile.settings.get_safe("os")
        if str(arch) in ['x86_64', 'sparcv9', 's390x']:
            return '-m64'
        elif str(arch) in ['x86', 'sparc']:
            return '-m32'
        elif str(arch) in ['s390']:
            return '-m31'
        elif str(the_os) == 'AIX':
            if str(arch) in ['ppc32']:
                return '-maix32'
            elif str(arch) in ['ppc64']:
                return '-maix64'
        return None


class AppleClangCompilerMixin(UnixCompilerMixin):
    compiler_name = 'apple-clang'

    @property
    def libcxx(self):
        libcxx = self._conanfile.settings.get_safe("compiler.libcxx")
        return "-stdlib={}".format(libcxx)


class ClangCompilerMixin(UnixCompilerMixin):
    compiler_name = 'clang'

    @property
    def libcxx(self):
        libcxx = self._conanfile.settings.get_safe("compiler.libcxx")
        if libcxx == "libc++":
            return "-stdlib=libc++"
        elif libcxx == "libstdc++" or libcxx == "libstdc++11":
            return "-stdlib=libstdc++"
        return None


class SunCCCompilerMixin(UnixCompilerMixin):
    compiler_name = 'sun-cc'

    @property
    def libcxx(self):
        libcxx = self._conanfile.settings.get_safe("compiler.libcxx")
        lib = {"libCstd": "Cstd",
               "libstdcxx": "stdcxx4",
               "libstlport": "stlport4",
               "libstdc++": "stdcpp"
               }.get(libcxx)
        if lib:
            return "-library={}".format(lib)
        return None


class GccCompilerMixin(UnixCompilerMixin):
    compiler_name = 'gcc'
    compiler_blocks = UnixCompilerMixin.compiler_blocks + ['blocks/compiler/glibcxx.cmake']

    @property
    def glibcxx(self):
        libcxx = self._conanfile.settings.get_safe("compiler.libcxx")
        if libcxx == "libstdc++11":
            return "1"
        elif libcxx == "libstdc++":
            return "0"


def get_mixin(compiler_name):
    # TODO: If we really want to let the user inject behaviour into our hierarchy of classes,
    #   then we can turn this into a factory and allow registration from outside
    if compiler_name == IntelCompilerMixin.compiler_name:
        return IntelCompilerMixin
    elif compiler_name == AppleClangCompilerMixin.compiler_name:
        return AppleClangCompilerMixin
    elif compiler_name == ClangCompilerMixin.compiler_name:
        return ClangCompilerMixin
    elif compiler_name == SunCCCompilerMixin.compiler_name:
        return SunCCCompilerMixin
    elif compiler_name == GccCompilerMixin.compiler_name:
        return GccCompilerMixin
    else:
        return CompilerMixin
