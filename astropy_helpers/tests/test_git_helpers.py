import imp
import os
import re
import sys

from setuptools.sandbox import run_setup

from . import *


_DEV_VERSION_RE = re.compile(r'\d+\.\d+(?:\.\d+)?\.dev(\d+)')


TEST_VERSION_SETUP_PY = """\
#!/usr/bin/env python

from setuptools import setup

NAME = '_eva_'
VERSION = {version!r}
RELEASE = 'dev' not in VERSION

from astropy_helpers.git_helpers import get_git_devstr
from astropy_helpers.version_helpers import generate_version_py

if not RELEASE:
    VERSION += get_git_devstr(False)

generate_version_py(NAME, VERSION, RELEASE, False)

setup(name=NAME, version=VERSION, packages=['_eva_'])
"""


TEST_VERSION_INIT = """\
try:
    from .version import version as __version__
    from .version import githash as __githash__
except ImportError:
    __version__ = __githash__ = ''
"""


@pytest.fixture
def version_test_package(tmpdir, request, version='42.42.dev'):
    test_package = tmpdir.mkdir('test_package')
    test_package.join('setup.py').write(
        TEST_VERSION_SETUP_PY.format(version=version))
    test_package.mkdir('_eva_').join('__init__.py').write(TEST_VERSION_INIT)
    with test_package.as_cwd():
        run_cmd('git', ['init'])
        run_cmd('git', ['add', '--all'])
        run_cmd('git', ['commit', '-m', 'test package'])

    old_astropy_helpers = {}
    if 'astropy_helpers' in sys.modules:
        # Delete the astropy_helpers that was imported by running the tests so
        # as to not confuse the astropy_helpers that will be used in testing
        # the package
        for k, v in sys.modules.items():
            if k.startswith('astropy_helpers'):
                old_astropy_helpers[k] = v
        cleanup_import('astropy_helpers')

    if '' in sys.path:
        sys.path.remove('')

    sys.path.insert(0, '')

    def finalize(old_astropy_helpers=old_astropy_helpers):
        if old_astropy_helpers:
            sys.modules.update(old_astropy_helpers)

        cleanup_import('_eva_')

    request.addfinalizer(finalize)

    return test_package


def test_update_git_devstr(version_test_package, capsys):
    """Tests that the commit number in the package's version string updates
    after git commits even without re-running setup.py.
    """

    with version_test_package.as_cwd():
        run_setup('setup.py', ['--version'])

        stdout, stderr = capsys.readouterr()
        version = stdout.strip()

        m = _DEV_VERSION_RE.match(version)
        assert m, (
            "Stdout did not match the version string pattern:"
            "\n\n{0}\n\nStderr:\n\n{1}".format(stdout, stderr))
        revcount = int(m.group(1))

        import _eva_
        assert _eva_.__version__ == version

        # Make a silly git commit
        with open('.test', 'w'):
            pass

        run_cmd('git', ['add', '.test'])
        run_cmd('git', ['commit', '-m', 'test'])

        import _eva_.version
        imp.reload(_eva_.version)

    # Previously this checked packagename.__version__, but in order for that to
    # be updated we also have to re-import _astropy_init which could be tricky.
    # Checking directly that the packagename.version module was updated is
    # sufficient:
    m = _DEV_VERSION_RE.match(_eva_.version.version)
    assert m
    assert int(m.group(1)) == revcount + 1

    # This doesn't test astropy_helpers.get_helpers.update_git_devstr directly
    # since a copy of that function is made in packagename.version (so that it
    # can work without astropy_helpers installed).  In order to get test
    # coverage on the actual astropy_helpers copy of that function just call it
    # directly and compare to the value in packagename
    from astropy_helpers.git_helpers import update_git_devstr

    newversion = update_git_devstr(version, path=str(version_test_package))
    assert newversion == _eva_.version.version


