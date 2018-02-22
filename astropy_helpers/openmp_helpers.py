# This module defines functions that can be used to check whether OpenMP is
# available and if so what flags to use. To use this, import the
# add_openmp_flags_if_available function in a setup_package.py file where you
# are defining your extensions:
#
#     from astropy_helpers.openmp_helpers import add_openmp_flags_if_available
#
# then call it with a single extension as the only argument:
#
#     add_openmp_flags_if_available(extension)
#
# this will add the OpenMP flags if available.

from __future__ import absolute_import, print_function

import datetime
import glob
import os
import subprocess
import sys
import tempfile
import time

from distutils import log
from distutils.ccompiler import new_compiler
from distutils.sysconfig import customize_compiler, get_config_var
from distutils.errors import CompileError, LinkError

from .setup_helpers import get_compiler_option

__all__ = ['add_openmp_flags_if_available']


CCODE = """
#include <omp.h>
#include <stdio.h>
int main(void) {
  #pragma omp parallel
  printf("nthreads=%d\\n", omp_get_num_threads());
  return 0;
}
"""

def _get_flag_value_from_var(flag, var, delim=' '):
    """
    Utility to extract `flag` value from `os.environ[`var`]` or, if not present,
    from `distutils.sysconfig.get_config_var(`var`)`.
    E.g. to get include path: _get_flag_value_from_var('-I', 'CFLAGS')
    might return "/usr/local/include".

    Notes
    -----
    Not yet tested and therefore not yet supported on Windows
    """

    if sys.platform.startswith('win'):
        return None

    # Simple input validation
    if not var or not flag:
        return None
    l = len(flag)
    if not l:
        return None

    # Look for var in os.eviron
    try:
        flags = os.environ[var]
    except KeyError:
        flags = None
    
    # If os.environ was unsuccesful try in sysconfig
    if not flags:
        try:
            flags = get_config_var(var)
        except KeyError:
            return None

    # Extract flag from {var:value}
    if flags:
        for item in flags.split(delim):
            if flag in item[:l]:
                return item[l:]

    return None

def _get_include_path():
    return _get_flag_value_from_var('-I', 'CFLAGS')

def _get_library_path():
    return _get_flag_value_from_var('-L', 'LDFLAGS')

def get_openmp_flags():
    """
    Utility for returning compiler and linker flags possibly needed for
    OpenMP support.

    Returns
    -------
    result : `{'compiler_flags':<flags>, 'linker_flags':<flags>}`

    Notes
    -----
    The flags returned are not tested for validity, use
    `test_openmp_support(openmp_flags=get_openmp_flags())` to do so.
    """

    compile_flags = []
    include_path = _get_include_path()
    if include_path:
        compile_flags.append('-I' + include_path)

    link_flags = []
    lib_path = _get_library_path()
    if lib_path:
        link_flags.append('-L' + lib_path)

    if get_compiler_option() == 'msvc':
        compile_flags.append('-openmp')
    else:
        compile_flags.append('-fopenmp')
        link_flags.append('-fopenmp')
        if lib_path:
            link_flags.append('-Wl,-rpath,' + lib_path)

    return {'compiler_flags':compile_flags, 'linker_flags':link_flags}

def test_openmp_support(openmp_flags=None, silent=False):
    """
    Compile and run OpenMP test code to determine viable support.

    Parameters
    ----------
    openmp_flags : dictionary, optional
        Expecting `{'compiler_flags':<flags>, 'linker_flags':<flags>}`.
        These are passed as `extra_postargs` to `compile()` and
        `link_executable()` respectively.
    silent : bool, optional
        silence log warnings

    Returns
    -------
    result : bool
        `True` if the test passed, `False` otherwise.
    """

    ccompiler = new_compiler()
    customize_compiler(ccompiler)

    if not openmp_flags:
        # customize_compiler() extracts info from os.environ. If certain keys
        # exist it uses these plus those from sysconfig.get_config_vars().
        # If the key is missing in os.environ it is not extracted from 
        # sysconfig.get_config_var(). E.g. 'LDFLAGS' get left out, preventing
        # clang from finding libomp.dylib because -L<path> is not passed to linker.
        # Call get_openmp_flags() to get flags missed by customize_compiler().
        openmp_flags = get_openmp_flags()
    compile_flags = openmp_flags['compiler_flags'] if 'compiler_flags' in openmp_flags else None
    link_flags = openmp_flags['linker_flags'] if 'linker_flags' in openmp_flags else None

    tmp_dir = tempfile.mkdtemp()
    start_dir = os.path.abspath('.')

    try:
        os.chdir(tmp_dir)

        # Write test program
        with open('test_openmp.c', 'w') as f:
            f.write(CCODE)

        os.mkdir('objects')

        # Compile, link, and run test program
        ccompiler.compile(['test_openmp.c'], output_dir='objects', extra_postargs=compile_flags)
        ccompiler.link_executable(glob.glob(os.path.join('objects', '*' + ccompiler.obj_extension)), 'test_openmp', extra_postargs=link_flags)
        output = subprocess.check_output('./test_openmp').decode(sys.stdout.encoding or 'utf-8').splitlines()

        if 'nthreads=' in output[0]:
            nthreads = int(output[0].strip().split('=')[1])
            if len(output) == nthreads:
                is_openmp_supported = True
            else:
                if not silent:
                    log.warn("Unexpected number of lines from output of test OpenMP "
                             "program (output was {0})".format(output))
                is_openmp_supported = False
        else:
            if not silent:
                log.warn("Unexpected output from test OpenMP "
                         "program (output was {0})".format(output))
            is_openmp_supported = False
    except (CompileError, LinkError):
        is_openmp_supported = False

    finally:
        os.chdir(start_dir)
    
    return is_openmp_supported

def is_openmp_supported():
    """
    Utility to determine whether the build compiler
    has OpenMP support.
    """
    return test_openmp_support(silent=True)

def add_openmp_flags_if_available(extension):
    """
    Add OpenMP compilation flags, if supported (if not a warning will be
    printed to the console and no flags will be added.)

    Returns `True` if the flags were added, `False` otherwise.
    """

    openmp_flags = get_openmp_flags()
    using_openmp = test_openmp_support(openmp_flags=openmp_flags, silent=False)

    if using_openmp:
        compile_flags = openmp_flags['compiler_flags'] if 'compiler_flags' in openmp_flags else None
        link_flags = openmp_flags['linker_flags'] if 'linker_flags' in openmp_flags else None
        log.info("Compiling Cython/C/C++ extension with OpenMP support")
        extension.extra_compile_args.extend(compile_flags)
        extension.extra_link_args.extend(link_flags)
    else:
        log.warn("Cannot compile Cython extension with OpenMP, reverting to non-parallel code")

    return using_openmp

_IS_OPENMP_ENABLED_SRC = """
# Autogenerated by {packagetitle}'s setup.py on {timestamp!s}

def is_openmp_enabled():
    \'\'\'
    Autogenerated utility to determine, post build, whether the package
    was built with or without OpenMP support.
    \'\'\'
    return {return_bool}
"""[1:]

def generate_openmp_enabled_py(packagename, srcdir='.'):
    """
    Utility for creating openmp_enabled.py::is_openmp_enabled()
    used to determine, post build, whether the package was built
    with or without OpenMP support.
    """

    if packagename.lower() == 'astropy':
        packagetitle = 'Astropy'
    else:
        packagetitle = packagename

    epoch = int(os.environ.get('SOURCE_DATE_EPOCH', time.time()))
    timestamp = datetime.datetime.utcfromtimestamp(epoch)

    src = _IS_OPENMP_ENABLED_SRC.format(packagetitle=packagetitle,
                                        timestamp=timestamp,
                                        return_bool=is_openmp_supported())

    package_srcdir = os.path.join(srcdir, *packagename.split('.'))
    is_openmp_enabled_py = os.path.join(package_srcdir, 'openmp_enabled.py')
    with open(is_openmp_enabled_py, 'w') as f:
        f.write(src)
