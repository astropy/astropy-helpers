import os
import shutil
import subprocess as sp
import sys

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


@pytest.fixture
def testpackage(tmpdir):
    """Create a copy of the testpackage repository (containing the package
    template) in a tempdir and change directories to that temporary copy.

    Also ensures that any previous imports of the test package are unloaded
    from `sys.modules`.
    """

    tmp_package = tmpdir.join('testpackage')
    shutil.copytree(os.path.join(PACKAGE_DIR, 'testpackage'),
                    str(tmp_package))
    os.chdir(str(tmp_package))

    if 'packagename' in sys.modules:
        del sys.modules['packagename']

    if '' in sys.path:
        sys.path.remove('')

    sys.path.insert(0, '')

    return tmp_package
