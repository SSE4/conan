from .generic import CMakeGenericToolchain


def CMakeToolchain(conanfile, *args, **kwargs):
    return CMakeGenericToolchain(conanfile, *args, **kwargs)
