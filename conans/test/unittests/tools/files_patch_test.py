import os
import unittest
from textwrap import dedent

from parameterized.parameterized import parameterized

from conans.client.graph.python_requires import ConanPythonRequire
from conans.client.loader import ConanFileLoader
from conans.test.utils.test_files import temp_folder
from conans.test.utils.tools import TestClient, TestBufferConanOutput,\
    test_processed_profile
from conans.util.files import save, load

base_conanfile = '''
from conans import ConanFile
from conans.tools import patch, replace_in_file
import os

class ConanFileToolsTest(ConanFile):
    name = "test"
    version = "1.9.10"
'''


class ToolsFilesPatchTest(unittest.TestCase):

    def test_patch1(self):
        patch_content = """From d0586e88122f41cd5ac9666db70c37d6f0fc7480 Mon Sep 17 00:00:00 2001
From: Peter Dimov <pdimov@gmail.com>
Date: Sun, 26 May 2019 18:49:12 +0300
Subject: [PATCH] Fix `bcp --namespace` issues

---
 Jamroot | 5 +++--
 1 file changed, 3 insertions(+), 2 deletions(-)

diff --git a/Jamroot b/Jamroot
index e0d7c90f51d..4e913c2b3f3 100644
--- a/Jamroot
+++ b/Jamroot
@@ -140,7 +140,8 @@ import "class" : new ;
 import property-set ;
 import threadapi-feature ;
 import option ;
-import tools/boost_install/boost-install ;
+# Backslash because of `bcp --namespace`
+import tools/boost\_install/boost-install ;
 
 path-constant BOOST_ROOT : . ;
 constant BOOST_VERSION : 1.71.0 ;
@@ -311,8 +312,8 @@ rule boost-install ( libraries * )
 # stage and install targets via boost-install, above.
 rule boost-lib ( name : sources * : requirements * : default-build * : usage-requirements * )
 {
+    autolink = <link>shared:<define>BOOST_$(name:U)_DYN_LINK=1 ;
     name = boost_$(name) ;
-    autolink = <link>shared:<define>$(name:U)_DYN_LINK=1 ;
     lib $(name)
         : $(sources)
         : $(requirements) $(autolink)
"""
        file_content = """# Copyright Vladimir Prus 2002-2006.
# Copyright Dave Abrahams 2005-2006.
# Copyright Rene Rivera 2005-2007.
# Copyright Douglas Gregor 2005.
#
# Distributed under the Boost Software License, Version 1.0.
# (See accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

# Usage:
#
#   b2 [options] [properties] [install|stage]
#
#   Builds and installs Boost.
#
# Targets and Related Options:
#
#   install                 Install headers and compiled library files to the
#   =======                 configured locations (below).
#
#   --prefix=<PREFIX>       Install architecture independent files here.
#                           Default: C:\Boost on Windows
#                           Default: /usr/local on Unix, Linux, etc.
#
#   --exec-prefix=<EPREFIX> Install architecture dependent files here.
#                           Default: <PREFIX>
#
#   --libdir=<LIBDIR>       Install library files here.
#                           Default: <EPREFIX>/lib
#
#   --includedir=<HDRDIR>   Install header files here.
#                           Default: <PREFIX>/include
#
#   --cmakedir=<CMAKEDIR>   Install CMake configuration files here.
#                           Default: <LIBDIR>/cmake
#
#   --no-cmake-config       Do not install CMake configuration files.
#
#   stage                   Build and install only compiled library files to the
#   =====                   stage directory.
#
#   --stagedir=<STAGEDIR>   Install library files here
#                           Default: ./stage
#
# Other Options:
#
#   --build-type=<type>     Build the specified pre-defined set of variations of
#                           the libraries. Note, that which variants get built
#                           depends on what each library supports.
#
#                               -- minimal -- (default) Builds a minimal set of
#                               variants. On Windows, these are static
#                               multithreaded libraries in debug and release
#                               modes, using shared runtime. On Linux, these are
#                               static and shared multithreaded libraries in
#                               release mode.
#
#                               -- complete -- Build all possible variations.
#
#   --build-dir=DIR         Build in this location instead of building within
#                           the distribution tree. Recommended!
#
#   --show-libraries        Display the list of Boost libraries that require
#                           build and installation steps, and then exit.
#
#   --layout=<layout>       Determine whether to choose library names and header
#                           locations such that multiple versions of Boost or
#                           multiple compilers can be used on the same system.
#
#                               -- versioned -- Names of boost binaries include
#                               the Boost version number, name and version of
#                               the compiler and encoded build properties. Boost
#                               headers are installed in a subdirectory of
#                               <HDRDIR> whose name contains the Boost version
#                               number.
#
#                               -- tagged -- Names of boost binaries include the
#                               encoded build properties such as variant and
#                               threading, but do not including compiler name
#                               and version, or Boost version. This option is
#                               useful if you build several variants of Boost,
#                               using the same compiler.
#
#                               -- system -- Binaries names do not include the
#                               Boost version number or the name and version
#                               number of the compiler. Boost headers are
#                               installed directly into <HDRDIR>. This option is
#                               intended for system integrators building
#                               distribution packages.
#
#                           The default value is 'versioned' on Windows, and
#                           'system' on Unix.
#
#   --buildid=ID            Add the specified ID to the name of built libraries.
#                           The default is to not add anything.
#
#   --python-buildid=ID     Add the specified ID to the name of built libraries
#                           that depend on Python. The default is to not add
#                           anything. This ID is added in addition to --buildid.
#
#   --help                  This message.
#
#   --with-<library>        Build and install the specified <library>. If this
#                           option is used, only libraries specified using this
#                           option will be built.
#
#   --without-<library>     Do not build, stage, or install the specified
#                           <library>. By default, all libraries are built.
#
# Properties:
#
#   toolset=toolset         Indicate the toolset to build with.
#
#   variant=debug|release   Select the build variant
#
#   link=static|shared      Whether to build static or shared libraries
#
#   threading=single|multi  Whether to build single or multithreaded binaries
#
#   runtime-link=static|shared
#                           Whether to link to static or shared C and C++
#                           runtime.
#

# TODO:
#  - handle boost version
#  - handle python options such as pydebug

import boostcpp ;
import package ;

import sequence ;
import xsltproc ;
import set ;
import path ;
import link ;
import notfile ;
import virtual-target ;
import "class" : new ;
import property-set ;
import threadapi-feature ;
import option ;
import tools/boost_install/boost-install ;

path-constant BOOST_ROOT : . ;
constant BOOST_VERSION : 1.70.0 ;
constant BOOST_JAMROOT_MODULE : $(__name__) ;

boostcpp.set-version $(BOOST_VERSION) ;

use-project /boost/architecture : libs/config/checks/architecture ;

local all-headers =
    [ MATCH .*libs/(.*)/include/boost : [ glob libs/*/include/boost libs/*/*/include/boost ] ] ;

for dir in $(all-headers)
{
    link-directory $(dir)-headers : libs/$(dir)/include/boost : <location>. ;
    explicit $(dir)-headers ;
}

if $(all-headers)
{
    constant BOOST_MODULARLAYOUT : $(all-headers) ;
}

project boost
    : requirements <include>.

      [ boostcpp.architecture ]
      [ boostcpp.address-model ]

      # Disable auto-linking for all targets here, primarily because it caused
      # troubles with V2.
      <define>BOOST_ALL_NO_LIB=1
      # Used to encode variant in target name. See the 'tag' rule below.
      <tag>@$(__name__).tag
      <conditional>@handle-static-runtime
      # Comeau does not support shared lib
      <toolset>como:<link>static
      <toolset>como-linux:<define>_GNU_SOURCE=1
      # When building docs within Boost, we want the standard Boost style
      <xsl:param>boost.defaults=Boost
      <conditional>@threadapi-feature.detect
    : usage-requirements <include>.
    : default-build
      <visibility>hidden
      <threading>multi
    : build-dir bin.v2
    ;

# This rule is called by Boost.Build to determine the name of target. We use it
# to encode the build variant, compiler name and boost version in the target
# name.
#
rule tag ( name : type ? : property-set )
{
    return [ boostcpp.tag $(name) : $(type) : $(property-set) ] ;
}

rule python-tag ( name : type ? : property-set )
{
    return [ boostcpp.python-tag $(name) : $(type) : $(property-set) ] ;
}

rule handle-static-runtime ( properties * )
{
    # Using static runtime with shared libraries is impossible on Linux, and
    # dangerous on Windows. Therefore, we disallow it. This might be drastic,
    # but it was disabled for a while without anybody complaining.

    # For CW, static runtime is needed so that std::locale works.
    if <link>shared in $(properties) && <runtime-link>static in $(properties) &&
        ! ( <toolset>cw in $(properties) )
    {
        if ! $(.shared-static-warning-emitted)
        {
            ECHO "warning: skipping configuration link=shared, runtime-link=static" ;
            ECHO "warning: this combination is either impossible or too dangerous" ;
            ECHO "warning: to be of any use" ;
            .shared-static-warning-emitted = 1 ;
        }

        return <build>no ;
    }
}

all-libraries = [ MATCH .*libs/(.*)/build/.* : [ glob libs/*/build/Jamfile.v2 ]
    [ glob libs/*/build/Jamfile ] ] ;

all-libraries = [ sequence.unique $(all-libraries) ] ;
# The function_types library has a Jamfile, but it's used for maintenance
# purposes, there's no library to build and install.
all-libraries = [ set.difference $(all-libraries) : function_types ] ;

# Setup convenient aliases for all libraries.

local rule explicit-alias ( id : targets + )
{
    alias $(id) : $(targets) ;
    explicit $(id) ;
}

# First, the complicated libraries: where the target name in Jamfile is
# different from its directory name.
explicit-alias prg_exec_monitor : libs/test/build//boost_prg_exec_monitor ;
explicit-alias test_exec_monitor : libs/test/build//boost_test_exec_monitor ;
explicit-alias unit_test_framework : libs/test/build//boost_unit_test_framework ;
explicit-alias bgl-vis : libs/graps/build//bgl-vis ;
explicit-alias serialization : libs/serialization/build//boost_serialization ;
explicit-alias wserialization : libs/serialization/build//boost_wserialization ;
for local l in $(all-libraries)
{
    if ! $(l) in test graph serialization headers
    {
        explicit-alias $(l) : libs/$(l)/build//boost_$(l) ;
    }
}

# Log has an additional target
explicit-alias log_setup : libs/log/build//boost_log_setup ;

rule do-nothing { }

rule generate-alias ( project name : property-set : sources * )
{
    local action-name = [ $(property-set).get <action> ] ;
    local m = [ MATCH ^@(.*) : $(action-name) ] ;
    property-set = [ property-set.empty ] ;
    local action = [ new action $(sources) : $(m[1]) : $(property-set) ] ;
    local t = [ new notfile-target $(name) : $(project) : $(action) ] ;
    return [ virtual-target.register $(t) ] ;
}

generate headers : $(all-headers)-headers : <generating-rule>@generate-alias <action>@do-nothing : : <include>.  ;

#alias headers : $(all-headers)-headers : : : <include>.  ;
explicit headers ;

# Make project ids of all libraries known.
for local l in $(all-libraries)
{
    use-project /boost/$(l) : libs/$(l)/build ;
}

if [ path.exists $(BOOST_ROOT)/tools/inspect/build ]
{
    use-project /boost/tools/inspect : tools/inspect/build ;
}

if [ path.exists $(BOOST_ROOT)/libs/wave/tool/build ]
{
    use-project /boost/libs/wave/tool : libs/wave/tool/build ;
}

# Make the boost-install rule visible in subprojects

# This rule should be called from libraries' Jamfiles and will create two
# targets, "install" and "stage", that will install or stage that library. The
# --prefix option is respected, but --with and --without options, naturally, are
# ignored.
#
# - libraries -- list of library targets to install.

rule boost-install ( libraries * )
{
    boost-install.boost-install $(libraries) ;
}

# Creates a library target, adding autolink support and also creates
# stage and install targets via boost-install, above.
rule boost-lib ( name : sources * : requirements * : default-build * : usage-requirements * )
{
    name = boost_$(name) ;
    autolink = <link>shared:<define>$(name:U)_DYN_LINK=1 ;
    lib $(name)
        : $(sources)
        : $(requirements) $(autolink)
        : $(default-build)
        : $(usage-requirements) $(autolink)
        ;
    boost-install $(name) ;
}


# Declare special top-level targets that build and install the desired variants
# of the libraries.
boostcpp.declare-targets $(all-libraries) ;
"""
        conanfile_content = """from conans import ConanFile, tools
class PatchConan(ConanFile):
    def source(self):
        tools.patch(self.source_folder, "p1.patch", strip=1)"""

        client = TestClient()
        client.save({"conanfile.py": conanfile_content,
                     "Jamroot": file_content,
                     "p1.patch": patch_content})

        client.run("source .")

        path = os.path.join(client.current_folder, "Jamroot")

        content = load(path)
        self.assertNotIn("constant BOOST_VERSION : 1.71.0 ;", content)
        self.assertIn("constant BOOST_VERSION : 1.70.0 ;", content)


    @parameterized.expand([(0, ), (1, )])
    def test_patch_from_file(self, strip):
        if strip:
            file_content = base_conanfile + '''
    def build(self):
        patch(patch_file="file.patch", strip=%s)
''' % strip
            patch_content = '''--- %s/text.txt\t2016-01-25 17:57:11.452848309 +0100
+++ %s/text_new.txt\t2016-01-25 17:57:28.839869950 +0100
@@ -1 +1 @@
-ONE TWO THREE
+ONE TWO FOUR''' % ("old_path", "new_path")
        else:
            file_content = base_conanfile + '''
    def build(self):
        patch(patch_file="file.patch")
'''
            patch_content = '''--- text.txt\t2016-01-25 17:57:11.452848309 +0100
+++ text_new.txt\t2016-01-25 17:57:28.839869950 +0100
@@ -1 +1 @@
-ONE TWO THREE
+ONE TWO FOUR'''

        tmp_dir, file_path, text_file = self._save_files(file_content)
        patch_file = os.path.join(tmp_dir, "file.patch")
        save(patch_file, patch_content)
        self._build_and_check(tmp_dir, file_path, text_file, "ONE TWO FOUR")

    def test_patch_from_str(self):
        file_content = base_conanfile + '''
    def build(self):
        patch_content = \'''--- text.txt\t2016-01-25 17:57:11.452848309 +0100
+++ text_new.txt\t2016-01-25 17:57:28.839869950 +0100
@@ -1 +1 @@
-ONE TWO THREE
+ONE TWO DOH!\'''
        patch(patch_string=patch_content)

'''
        tmp_dir, file_path, text_file = self._save_files(file_content)
        self._build_and_check(tmp_dir, file_path, text_file, "ONE TWO DOH!")

    def test_patch_strip_new(self):
        conanfile = dedent("""
            from conans import ConanFile, tools
            class PatchConan(ConanFile):
                def source(self):
                    tools.patch(self.source_folder, "example.patch", strip=1)""")
        patch = dedent("""
            --- /dev/null
            +++ b/src/newfile
            @@ -0,0 +0,1 @@
            +New file!""")

        client = TestClient()
        client.save({"conanfile.py": conanfile,
                     "example.patch": patch})
        client.run("source .")
        self.assertEqual(load(os.path.join(client.current_folder, "newfile")),
                         "New file!")

    def test_patch_strip_delete(self):
        conanfile = dedent("""
            from conans import ConanFile, tools
            class PatchConan(ConanFile):
                def source(self):
                    tools.patch(self.source_folder, "example.patch", strip=1)""")
        patch = dedent("""
            --- a\src\oldfile
            +++ b/dev/null
            @@ -0,1 +0,0 @@
            -legacy code""")
        client = TestClient()
        client.save({"conanfile.py": conanfile,
                     "example.patch": patch,
                     "oldfile": "legacy code"})
        path = os.path.join(client.current_folder, "oldfile")
        self.assertTrue(os.path.exists(path))
        client.run("source .")
        self.assertFalse(os.path.exists(path))

    def test_patch_strip_delete_no_folder(self):
        conanfile = dedent("""
            from conans import ConanFile, tools
            class PatchConan(ConanFile):
                def source(self):
                    tools.patch(self.source_folder, "example.patch", strip=1)""")
        patch = dedent("""
            --- a/oldfile
            +++ b/dev/null
            @@ -0,1 +0,0 @@
            -legacy code""")
        client = TestClient()
        client.save({"conanfile.py": conanfile,
                     "example.patch": patch,
                     "oldfile": "legacy code"})
        path = os.path.join(client.current_folder, "oldfile")
        self.assertTrue(os.path.exists(path))
        client.run("source .")
        self.assertFalse(os.path.exists(path))

    def test_patch_new_delete(self):
        conanfile = base_conanfile + '''
    def build(self):
        from conans.tools import load, save
        save("oldfile", "legacy code")
        assert(os.path.exists("oldfile"))
        patch_content = """--- /dev/null
+++ b/newfile
@@ -0,0 +0,3 @@
+New file!
+New file!
+New file!
--- a/oldfile
+++ b/dev/null
@@ -0,1 +0,0 @@
-legacy code
"""
        patch(patch_string=patch_content)
        self.output.info("NEW FILE=%s" % load("newfile"))
        self.output.info("OLD FILE=%s" % os.path.exists("oldfile"))
'''
        client = TestClient()
        client.save({"conanfile.py": conanfile})
        client.run("create . user/testing")
        self.assertIn("test/1.9.10@user/testing: NEW FILE=New file!\nNew file!\nNew file!\n",
                      client.out)
        self.assertIn("test/1.9.10@user/testing: OLD FILE=False", client.out)

    def test_patch_new_strip(self):
        conanfile = base_conanfile + '''
    def build(self):
        from conans.tools import load, save
        patch_content = """--- /dev/null
+++ b/newfile
@@ -0,0 +0,3 @@
+New file!
+New file!
+New file!
"""
        patch(patch_string=patch_content, strip=1)
        self.output.info("NEW FILE=%s" % load("newfile"))
'''
        client = TestClient()
        client.save({"conanfile.py": conanfile})
        client.run("create . user/testing")
        self.assertIn("test/1.9.10@user/testing: NEW FILE=New file!\nNew file!\nNew file!\n",
                      client.out)

    def test_error_patch(self):
        file_content = base_conanfile + '''
    def build(self):
        patch_content = "some corrupted patch"
        patch(patch_string=patch_content, output=self.output)

'''
        client = TestClient()
        client.save({"conanfile.py": file_content})
        client.run("install .")
        client.run("build .", assert_error=True)
        self.assertIn("patch_ng: error: no patch data found!", client.out)
        self.assertIn("ERROR: conanfile.py (test/1.9.10): "
                      "Error in build() method, line 12", client.out)
        self.assertIn("Failed to parse patch: string", client.out)

    def test_add_new_file(self):
        """ Validate issue #5320
        """

        conanfile = dedent("""
            from conans import ConanFile, tools
            import os
            
            class ConanFileToolsTest(ConanFile):
                name = "foobar"
                version = "0.1.0"
                exports_sources = "*"
            
                def build(self):
                    tools.patch(patch_file="add_files.patch")
                    assert os.path.isfile("foo.txt")
                    assert os.path.isfile("bar.txt")
        """)
        bar = "no creo en brujas"
        patch = dedent("""
            From c66347c66991b6e617d107b505c18b3115624b8a Mon Sep 17 00:00:00 2001
            From: Uilian Ries <uilianries@gmail.com>
            Date: Wed, 16 Oct 2019 14:31:34 -0300
            Subject: [PATCH] add foo
            
            ---
             bar.txt | 3 ++-
             foo.txt | 3 +++
             2 files changed, 5 insertions(+), 1 deletion(-)
             create mode 100644 foo.txt
            
            diff --git a/bar.txt b/bar.txt
            index 0f4ff3a..0bd3158 100644
            --- a/bar.txt
            +++ b/bar.txt
            @@ -1 +1,2 @@
            -no creo en brujas
            +Yo no creo en brujas, pero que las hay, las hay
            +
            diff --git a/foo.txt b/foo.txt
            new file mode 100644
            index 0000000..91e8c0d
            --- /dev/null
            +++ b/foo.txt
            @@ -0,0 +1,3 @@
            +For us, there is no spring.
            +Just the wind that smells fresh before the storm.
            +
            -- 
            2.23.0


        """)

        client = TestClient()
        client.save({"conanfile.py": conanfile,
                     "add_files.patch": patch,
                     "bar.txt": bar})
        client.run("install .")
        client.run("build .")
        bar_content = load(os.path.join(client.current_folder, "bar.txt"))
        self.assertIn(dedent("""Yo no creo en brujas, pero que las hay, las hay
                             """), bar_content)
        foo_content = load(os.path.join(client.current_folder, "foo.txt"))
        self.assertIn(dedent("""For us, there is no spring.
Just the wind that smells fresh before the storm."""), foo_content)
        self.assertIn("Running build()", client.out)
        self.assertNotIn("Warning", client.out)

    def _save_files(self, file_content):
        tmp_dir = temp_folder()
        file_path = os.path.join(tmp_dir, "conanfile.py")
        text_file = os.path.join(tmp_dir, "text.txt")
        save(file_path, file_content)
        save(text_file, "ONE TWO THREE")
        return tmp_dir, file_path, text_file

    def _build_and_check(self, tmp_dir, file_path, text_file, msg):
        loader = ConanFileLoader(None, TestBufferConanOutput(), ConanPythonRequire(None, None))
        ret = loader.load_consumer(file_path, test_processed_profile())
        curdir = os.path.abspath(os.curdir)
        os.chdir(tmp_dir)
        try:
            ret.build()
        finally:
            os.chdir(curdir)

        content = load(text_file)
        self.assertEqual(content, msg)
