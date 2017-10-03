import os
from distutils.core import Extension

from ..openmp_helpers import add_openmp_flags_if_available
from ..setup_helpers import register_commands

IS_TRAVIS_LINUX = os.environ.get('TRAVIS_OS_NAME', None) == 'linux'
IS_APPVEYOR = os.environ.get('APPVEYOR', None) == 'True'


def test_add_openmp_flags_if_available():

    register_commands('yoda', '0.0', False)

    using_openmp = add_openmp_flags_if_available(Extension('test', []))

    # Make sure that on Travis (Linux) and AppVeyor OpenMP does get used (for
    # MacOS X usually it will not work but this will depend on the compiler).
    # Having this is useful because we'll find out if OpenMP no longer works
    # for any reason on platforms on which it does work at the time of writing.
    if IS_TRAVIS_LINUX or IS_APPVEYOR:
        assert using_openmp
