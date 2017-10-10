import os
import sys
from copy import deepcopy
from distutils.core import Extension

from ..openmp_helpers import add_openmp_flags_if_available
from ..setup_helpers import _module_state, register_commands

IS_TRAVIS_LINUX = os.environ.get('TRAVIS_OS_NAME', None) == 'linux'
IS_APPVEYOR = os.environ.get('APPVEYOR', None) == 'True'
PY3_LT_35 = sys.version_info[0] == 3 and sys.version_info[1] < 5

_state = None


def setup_function(function):
    global state
    state = deepcopy(_module_state)


def teardown_function(function):
    _module_state.clear()
    _module_state.update(state)


def test_add_openmp_flags_if_available():

    register_commands('openmp_testing', '0.0', False)

    using_openmp = add_openmp_flags_if_available(Extension('test', []))

    # Make sure that on Travis (Linux) and AppVeyor OpenMP does get used (for
    # MacOS X usually it will not work but this will depend on the compiler).
    # Having this is useful because we'll find out if OpenMP no longer works
    # for any reason on platforms on which it does work at the time of writing.
    # OpenMP doesn't work on Python 3.x where x<5 on AppVeyor though.
    if IS_TRAVIS_LINUX or (IS_APPVEYOR and not PY3_LT_35):
        assert using_openmp
