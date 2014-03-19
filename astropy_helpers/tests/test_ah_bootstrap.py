import glob
import os
import textwrap

from setuptools.sandbox import run_setup

from . import run_cmd, testpackage
from ..utils import silence


TEST_SETUP_PY = """\
#!/usr/bin/env python
from __future__ import print_function

import os
import sys

import ah_bootstrap
# reset the name of the package installed by ah_boostrap to
# _astropy_helpers_test_--this will prevent any confusion by pkg_resources with
# any already installed packages named astropy_helpers
ah_bootstrap.DIST_NAME = 'astropy-helpers-test'
ah_bootstrap.PACKAGE_NAME = '_astropy_helpers_test_'
try:
    ah_bootstrap.use_astropy_helpers({args})
finally:
    ah_bootstrap.DIST_NAME = 'astropy-helpers'
    ah_bootstrap.PACKAGE_NAME = 'astropy_helpers'

import _astropy_helpers_test_
print(os.path.abspath(_astropy_helpers_test_.__file__))
"""


def test_bootstrap_from_submodule(tmpdir, testpackage, capsys):
    """
    Tests importing _astropy_helpers_test_ from a submodule in a git
    repository.  This tests actually performing a fresh clone of the repository
    without the submodule initialized, and that importing astropy_helpers in
    that context works transparently after calling
    `ah_boostrap.use_astropy_helpers`.
    """

    orig_repo = tmpdir.mkdir('orig')
    old_cwd = os.getcwd()

    # Ensure ah_bootstrap is imported from the local directory
    import ah_bootstrap

    try:
        os.chdir(str(orig_repo))
        run_cmd('git', ['init'])

        # Write a test setup.py that uses ah_bootstrap; it also ensures that
        # any previous reference to astropy_helpers is first wiped from
        # sys.modules
        orig_repo.join('setup.py').write(TEST_SETUP_PY.format(args=''))
        run_cmd('git', ['add', 'setup.py'])

        # Add our own clone of the astropy_helpers repo as a submodule named
        # astropy_helpers
        run_cmd('git', ['submodule', 'add', str(testpackage),
                        '_astropy_helpers_test_'])

        run_cmd('git', ['commit', '-m', 'test repository'])

        os.chdir(str(tmpdir))

        # Creates a clone of our test repo in the directory 'clone'
        run_cmd('git', ['clone', 'orig', 'clone'])

        os.chdir('clone')

        run_setup('setup.py', [])

        stdout, stderr = capsys.readouterr()
        path = stdout.strip()

        # Ensure that the astropy_helpers used by the setup.py is the one that
        # was imported from git submodule
        assert path == str(tmpdir.join('clone', '_astropy_helpers_test_',
                                       '_astropy_helpers_test_',
                                       '__init__.py'))
    finally:
        os.chdir(old_cwd)


def test_download_if_needed(tmpdir, testpackage, capsys):
    """
    Tests the case where astropy_helpers was not actually included in a
    package, or is otherwise missing, and we need to "download" it.

    This does not test actually downloading from the internet--this is normally
    done through setuptools' easy_install command which can also install from a
    source archive.  From the point of view of ah_boostrap the two actions are
    equivalent, so we can just as easily simulate this by providing a setup.cfg
    giving the path to a source archive to "download" (as though it were a
    URL).
    """

    source = tmpdir.mkdir('source')
    old_cwd = os.getcwd()

    # Ensure ah_bootstrap is imported from the local directory
    import ah_bootstrap

    os.chdir(str(testpackage))
    # Make a source distribution of the test package
    with silence():
        run_setup('setup.py', ['sdist', '--dist-dir=dist',
                               '--formats=gztar'])

    dist_dir = testpackage.join('dist')

    os.chdir(str(source))
    try:
        source.join('setup.py').write(TEST_SETUP_PY.format(args=''))
        source.join('setup.cfg').write(textwrap.dedent("""\
            [easy_install]
            find_links = {find_links}
        """.format(find_links=str(dist_dir))))

        run_setup('setup.py', [])

        stdout, stderr = capsys.readouterr()
        path = stdout.strip()

        # easy_install should have worked by 'installing' astropy_helpers as a
        # .egg in the current directory
        eggs = glob.glob('*.egg')
        assert eggs
        egg = source.join(eggs[0])
        assert os.path.isdir(str(egg))

        assert path == str(egg.join('_astropy_helpers_test_',
                                    '__init__.pyc'))
    finally:
        os.chdir(old_cwd)
