#
# buildbug is a debugger for 'osc build'
#
# (C) 2012, jw@suse.de, openSUSE.org
# Distribute under GPLv2 or GPLv3
#

import traceback
global OSC_BUILDBUG_PLUGIN_VERSION, OSC_BUILDBUG_PLUGIN_NAME
OSC_BUILDBUG_PLUGIN_VERSION = '0.01'
OSC_BUILDBUG_PLUGIN_NAME = traceback.extract_stack()[-1][0] + ' V' + OSC_BUILDBUG_PLUGIN_VERSION

@cmdln.alias('bbuild')
@cmdln.alias('bugbuild')
@cmdln.alias('bbug')
@cmdln.alias('bb')
@cmdln.option('--clean', action='store_true',
                  help='Delete old build root before initializing it')
@cmdln.option('-o', '--offline', action='store_true',
                  help='Start with cached prjconf and packages without contacting the api server')
@cmdln.option('-l', '--preload', action='store_true',
                  help='Preload all files into the chache for offline operation')
@cmdln.option('--no-changelog', action='store_true',
                  help='don\'t update the package changelog from a changes file')
@cmdln.option('--rsync-src', metavar='RSYNCSRCPATH', dest='rsyncsrc',
                  help='Copy folder to buildroot after installing all RPMs. Use together with --rsync-dest. This is the path on the HOST filesystem e.g. /tmp/linux-kernel-tree. It defines RSYNCDONE 1 .')
@cmdln.option('--rsync-dest', metavar='RSYNCDESTPATH', dest='rsyncdest',
                  help='Copy folder to buildroot after installing all RPMs. Use together with --rsync-src. This is the path on the TARGET filesystem e.g. /usr/src/packages/BUILD/linux-2.6 .')
@cmdln.option('--overlay', metavar='OVERLAY',
                  help='Copy overlay filesystem to buildroot after installing all RPMs .')
@cmdln.option('--noinit', '--no-init', action='store_true',
                  help='Skip initialization of build root and start with build immediately.')
@cmdln.option('--nochecks', '--no-checks', action='store_true',
                  help='Do not run post build checks on the resulting packages.')
@cmdln.option('--no-verify', action='store_true',
                  help='Skip signature verification of packages used for build. (Global config in .oscrc: no_verify)')
@cmdln.option('--noservice', '--no-service', action='store_true',
                  help='Skip run of local source services as specified in _service file.')
@cmdln.option('-p', '--prefer-pkgs', metavar='DIR', action='append',
                  help='Prefer packages from this directory when installing the build-root')
@cmdln.option('-k', '--keep-pkgs', metavar='DIR',
                  help='Save built packages into this directory')
@cmdln.option('-x', '--extra-pkgs', metavar='PAC', action='append',
                  help='Add this package when installing the build-root')
@cmdln.option('--root', metavar='ROOT',
                  help='Build in specified directory')
@cmdln.option('-j', '--jobs', metavar='N',
                  help='Compile with N jobs')
@cmdln.option('--icecream', metavar='N',
                  help='use N parallel build jobs with icecream')
@cmdln.option('--ccache', action='store_true',
                  help='use ccache to speed up rebuilds')
@cmdln.option('--with', metavar='X', dest='_with', action='append',
                  help='enable feature X for build')
@cmdln.option('--without', metavar='X', action='append',
                  help='disable feature X for build')
@cmdln.option('--define', metavar='\'X Y\'', action='append',
                  help='define macro X with value Y')
@cmdln.option('--userootforbuild', action='store_true',
                  help='Run build as root. The default is to build as '
                  'unprivileged user. Note that a line "# norootforbuild" '
                  'in the spec file will invalidate this option.')
@cmdln.option('--build-uid', metavar='uid:gid|"caller"',
                  help='specify the numeric uid:gid pair to assign to the '
                  'unprivileged "abuild" user or use "caller" to use the current user uid:gid')
@cmdln.option('--local-package', action='store_true',
                  help='build a package which does not exist on the server')
@cmdln.option('--linksources', action='store_true',
                  help='use hard links instead of a deep copied source')
@cmdln.option('--vm-type', metavar='TYPE',
                  help='use VM type TYPE (e.g. kvm)')
@cmdln.option('--alternative-project', metavar='PROJECT',
                  help='specify the build target project')
@cmdln.option('-d', '--debuginfo', action='store_true',
                  help='also build debuginfo sub-packages')
@cmdln.option('--disable-debuginfo', action='store_true',
                  help='disable build of debuginfo packages')
@cmdln.option('-b', '--baselibs', action='store_true',
                  help='Create -32bit/-64bit/-x86 rpms for other architectures')
@cmdln.option('--release', metavar='N',
                  help='set release number of the package to N')
@cmdln.option('--disable-cpio-bulk-download', action='store_true',
                  help='disable downloading packages as cpio archive from api')
@cmdln.option('--cpio-bulk-download', action='store_false',
                  dest='disable_cpio_bulk_download', help=SUPPRESS_HELP)
@cmdln.option('--download-api-only', action='store_true',
                  help=SUPPRESS_HELP)
@cmdln.option('--oldpackages', metavar='DIR',
            help='take previous build from DIR (special values: _self, _link)')
@cmdln.option('--shell', action='store_true',
                  help=SUPPRESS_HELP)
def do_buildbug(self, subcmd, opts, *args):
        """${cmd_name}: Build a package on your local machine

        
        osc buildbug is an experimental version of osc build. 
        both commands work exactly the same, except that buildbug has added debugging support.

        You need to call the command inside a package directory, which should be a
        buildsystem checkout. (Local modifications are fine.)

        The arguments REPOSITORY and ARCH can be taken from the first two columns
        of the 'osc repos' output. BUILD_DESCR is either a RPM spec file, or a
        Debian dsc file.

        Please study 'osc build --help' for more details.

        ${cmd_option_list}
        """
        from conf import config, cookiejar
        import tempfile

        opts.buildbug = True    # not used, maybe osc.build.main() wants to know we are here, someday.

        print OSC_BUILDBUG_PLUGIN_NAME
        (wrap_fd, wrap_name) = tempfile.mkstemp(suffix='-buildbug-wrap.sh')
        wrap = os.fdopen(wrap_fd, "w+b")
        os.fchmod(wrap_fd, 0755)
        print "buildbug: wrap='%s' build-cmd='%s'" % (wrap_name, config['build-cmd'])
        print >>wrap, """#! /bin/sh -x
#
# buildbug-wrap.sh written by %s
#
build_cmd=%s
echo "+ $build_cmd $@"
id -a

sleep 1
bash -x $build_cmd $@
""" % (OSC_BUILDBUG_PLUGIN_NAME, config['build-cmd'])
        
        ## prepare the trampoline
        #
        ## Ouch, as long as the filedescriptor is open, kernel refuses to exec the shell script, 
        ## ETXTBSY (Text file busy)
        ## (this can be seen with .oscrc:su-wrapper = strace)
        wrap.close()    # put our own rm at the end of the script.

        config['build-cmd'] = wrap_name

        # jump 
        r = self.do_build(subcmd, opts, *args)
        os.unlink(wrap_name)
        return r
