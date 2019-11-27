"""
This module contains various utilities for introspecting the distutils
module and the setup process.

Some of these utilities require the
`extension_helpers.setup_helpers.register_commands` function to be called first,
as it will affect introspection of setuptools command-line arguments.  Other
utilities in this module do not have that restriction.
"""

import os
import sys

from distutils import ccompiler, log
from distutils.dist import Distribution
from distutils.errors import DistutilsError

from .utils import silence


def get_dummy_distribution():
    """
    Returns a distutils Distribution object used to instrument the setup
    environment before calling the actual setup() function.
    """

    from .setup_helpers import _module_state

    # Pre-parse the Distutils command-line options and config files to if
    # the option is set.
    dist = Distribution({'script_name': os.path.basename(sys.argv[0]),
                         'script_args': sys.argv[1:]})

    with silence():
        try:
            dist.parse_config_files()
            dist.parse_command_line()
        except (DistutilsError, AttributeError, SystemExit):
            # Let distutils handle DistutilsErrors itself AttributeErrors can
            # get raise for ./setup.py --help SystemExit can be raised if a
            # display option was used, for example
            pass

    return dist


def get_main_package_directory(distribution):
    """
    Given a Distribution object, return the main package directory.
    """
    return min(distribution.packages, key=len).replace('.', os.sep)

def get_distutils_option(option, commands):
    """ Returns the value of the given distutils option.

    Parameters
    ----------
    option : str
        The name of the option

    commands : list of str
        The list of commands on which this option is available

    Returns
    -------
    val : str or None
        the value of the given distutils option. If the option is not set,
        returns None.
    """

    dist = get_dummy_distribution()

    for cmd in commands:
        cmd_opts = dist.command_options.get(cmd)
        if cmd_opts is not None and option in cmd_opts:
            return cmd_opts[option][1]
    else:
        return None


def get_distutils_build_option(option):
    """ Returns the value of the given distutils build option.

    Parameters
    ----------
    option : str
        The name of the option

    Returns
    -------
    val : str or None
        The value of the given distutils build option. If the option
        is not set, returns None.
    """
    return get_distutils_option(option, ['build', 'build_ext', 'build_clib'])


def get_compiler_option():
    """ Determines the compiler that will be used to build extension modules.

    Returns
    -------
    compiler : str
        The compiler option specified for the build, build_ext, or build_clib
        command; or the default compiler for the platform if none was
        specified.

    """

    compiler = get_distutils_build_option('compiler')
    if compiler is None:
        return ccompiler.get_default_compiler()

    return compiler
