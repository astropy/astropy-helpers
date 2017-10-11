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

import os
import sys
import glob
import tempfile
import subprocess

from distutils import log
from distutils.ccompiler import new_compiler
from distutils.sysconfig import customize_compiler
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


def add_openmp_flags_if_available(extension):
    """
    Add OpenMP compilation flags, if available (if not a warning will be
    printed to the console and no flags will be added)

    Returns `True` if the flags were added, `False` otherwise.
    """

    ccompiler = new_compiler()
    customize_compiler(ccompiler)

    tmp_dir = tempfile.mkdtemp()

    start_dir = os.path.abspath('.')

    if get_compiler_option() == 'msvc':
        compile_flag = '-openmp'
        link_flag = ''
    else:
        compile_flag = '-fopenmp'
        link_flag = '-fopenmp'

    try:

        os.chdir(tmp_dir)

        with open('test_openmp.c', 'w') as f:
            f.write(CCODE)

        os.mkdir('objects')

        # Compile, link, and run test program
        ccompiler.compile(['test_openmp.c'], output_dir='objects', extra_postargs=[compile_flag])
        ccompiler.link_executable(glob.glob(os.path.join('objects', '*')), 'test_openmp', extra_postargs=[link_flag])
        output = subprocess.check_output('./test_openmp').decode(sys.stdout.encoding or 'utf-8').splitlines()

        if 'nthreads=' in output[0]:
            nthreads = int(output[0].strip().split('=')[1])
            if len(output) == nthreads:
                using_openmp = True
            else:
                log.warn("Unexpected number of lines from output of test OpenMP "
                         "program (output was {0})".format(output))
                using_openmp = False
        else:
            log.warn("Unexpected output from test OpenMP "
                     "program (output was {0})".format(output))
            using_openmp = False

    except (CompileError, LinkError):

        using_openmp = False

    finally:

        os.chdir(start_dir)

    if using_openmp:
        log.info("Compiling Cython extension with OpenMP support")
        extension.extra_compile_args.append(compile_flag)
        extension.extra_link_args.append(link_flag)
    else:
        log.warn("Cannot compile Cython extension with OpenMP, reverting to non-parallel code")

    return using_openmp
