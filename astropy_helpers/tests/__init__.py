import os
import shutil
import subprocess as sp
import sys

from setuptools.sandbox import run_setup

import pytest

PACKAGE_DIR = os.path.dirname(__file__)


def run_cmd(cmd, args, path=None):
    """
    Runs a shell command with the given argument list.  Changes directory to
    ``path`` if given, otherwise runs the command in the current directory.

    Returns a 3-tuple of (stdout, stderr, exit code)
    """

    if path is not None:
        # Transparently support py.path objects
        path = str(path)

    p = sp.Popen([cmd] + list(args), stdout=sp.PIPE, stderr=sp.PIPE,
                 cwd=path)
    streams = tuple(s.decode('latin1').strip() for s in p.communicate())
    return streams + (p.returncode,)


@pytest.fixture(scope='function', autouse=True)
def reset_distutils_log():
    """
    This is a setup/teardown fixture that ensures the log-level of the
    distutils log is always set to a default of WARN, since different
    settings could affect tests that check the contents of stdout.
    """

    from distutils import log
    log.set_threshold(log.WARN)


@pytest.fixture
def package_template(tmpdir, request):
    """Create a copy of the package_template repository (containing the package
    template) in a tempdir and change directories to that temporary copy.

    Also ensures that any previous imports of the test package are unloaded
    from `sys.modules`.
    """

    tmp_package = tmpdir.join('package_template')
    shutil.copytree(os.path.join(PACKAGE_DIR, 'package_template'),
                    str(tmp_package))

    def finalize(old_cwd=os.getcwd()):
        os.chdir(old_cwd)

    # Before changing directores import the local ah_boostrap module so that it
    # is tested, and *not* the copy that happens to be included in the test
    # package

    import ah_bootstrap

    os.chdir(str(tmp_package))

    if 'packagename' in sys.modules:
        del sys.modules['packagename']

    if '' in sys.path:
        sys.path.remove('')

    sys.path.insert(0, '')

    request.addfinalizer(finalize)

    return tmp_package


TEST_PACKAGE_SETUP_PY = """\
#!/usr/bin/env python

from setuptools import setup

setup(name='astropy-helpers-test', version='0.0',
      packages=['_astropy_helpers_test_'],
      zip_safe=False)
"""


@pytest.fixture
def testpackage(tmpdir):
    """
    This fixture creates a simplified package called _astropy_helpers_test_
    used primarily for testing ah_boostrap, but without using the
    astropy_helpers package directly and getting it confused with the
    astropy_helpers package already under test.
    """

    old_cwd = os.path.abspath(os.getcwd())
    source = tmpdir.mkdir('testpkg')

    os.chdir(str(source))
    try:

        source.mkdir('_astropy_helpers_test_')
        source.ensure('_astropy_helpers_test_', '__init__.py')
        source.join('setup.py').write(TEST_PACKAGE_SETUP_PY)

        # Make the new test package into a git repo
        run_cmd('git', ['init'])
        run_cmd('git', ['add', '--all'])
        run_cmd('git', ['commit', '-m', 'test package'])

    finally:
        os.chdir(old_cwd)

    return source


# Ugly workaround:
# setuptools includes a copy of tempfile.TemporaryDirectory for older Python
# versions that do not have that class.  But the copy included in setuptools is
# affected by this bug:  http://bugs.python.org/issue10188
# Patch setuptools' TemporaryDirectory so that it doesn't crash on shutdown
class TemporaryDirectory(object):
    """"
    Very simple temporary directory context manager.
    Will try to delete afterward, but will also ignore OS and similar
    errors on deletion.
    """
    def __init__(self):
        import tempfile
        self.name = None # Handle mkdtemp raising an exception
        self.name = tempfile.mkdtemp()

    def __enter__(self):
        return self.name

    def __exit__(self, exctype, excvalue, exctrace):
        import shutil
        try:
            shutil.rmtree(self.name, True)
        except OSError: #removal errors are not the only possible
            pass
        self.name = None

try:
    from tempfile import TemporaryDirectory
except ImportError:
    import setuptools.py31compat
    setuptools.py31compat.TemporaryDirectory = TemporaryDirectory
