# This module defines functions that can be used to check whether OpenMP is
# available and if so what flags to use.

# This file includes code adapted from astroscrappy, originally released under
# the following license:
#
# Copyright (c) 2015, Curtis McCully
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice, this
#   list of conditions and the following disclaimer in the documentation and/or
#   other materials provided with the distribution.
# * Neither the name of the Astropy Team nor the names of its contributors may be
#   used to endorse or promote products derived from this software without
#   specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from __future__ import absolute_import, print_function

import os
import tempfile
import subprocess

from distutils import log
from distutils.ccompiler import new_compiler
from distutils.sysconfig import customize_compiler
from distutils.errors import CompileError, LinkError

from .setup_helpers import get_compiler_option

__all__ = ['add_openmp_flags_if_available']


def add_openmp_flags_if_available(extension):
    """
    Add OpenMP compilation flags, if available (if not a warning will be
    printed to the console and no flags will be added)

    Returns `True` if the flags were added, `False` otherwise.
    """

    ccompiler = new_compiler()
    customize_compiler(ccompiler)

    tmp_dir = tempfile.mkdtemp()

    CCODE = """
    #include <omp.h>
    #include <stdio.h>
    int main() {
    #pragma omp parallel
    printf("nthreads=%d\\n", omp_get_num_threads());
    }
    """

    start_dir = os.path.abspath('.')

    if get_compiler_option() == 'msvc':
        flag = '-openmp'
    else:
        flag = '-fopenmp'

    try:

        os.chdir(tmp_dir)

        with open('test_openmp.c', 'w') as f:
            f.write(CCODE)

        # Compile, link, and run test program
        ccompiler.compile(['test_openmp.c'], output_dir='.', extra_postargs=[flag])
        ccompiler.link_executable(['test_openmp.o'], 'test_openmp', extra_postargs=[flag])
        output = subprocess.check_output('./test_openmp').decode('utf-8').splitlines()

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
        log.info("Compiling Cython extension with OpenMP support (using {0} flag)".format(flag))
        extension.extra_compile_args.append(flag)
        if get_compiler_option() != 'msvc':
            extension.extra_link_args.append(flag)
    else:
        log.warn("Cannot compile Cython extension with OpenMP, reverting to non-parallel code")

    return using_openmp
