from conans.client.tools.files import save


def create_cmake_module_alias_targets(_, module, targets):
    content = ""
    for alias, aliased in targets.items():
        content += "if(TARGET {aliased} AND NOT TARGET {alias})\n" \
                   "    add_library({alias} INTERFACE IMPORTED)\n" \
                   "    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})\n" \
                   "endif()\n".format(alias=alias, aliased=aliased)
    save(module, content)
