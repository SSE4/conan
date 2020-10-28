class OSBuildDefaultMixin(object):
    _conanfile = None


class XBuildingMixin(OSBuildDefaultMixin):
    osbuild_blocks = ['blocks/osbuild/crossbuild.cmake']

    @property
    def cmake_system_name(self):
        return self._conanfile.settings.os


def get_mixin(osbuild_name, xbuilding=False):
    # TODO: If we really want to let the user inject behaviour into our hierarchy of classes,
    #   then we can turn this into a factory and allow registration from outside
    if xbuilding:
        return XBuildingMixin
    return OSBuildDefaultMixin
