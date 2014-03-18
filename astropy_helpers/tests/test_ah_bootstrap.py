import os

from setuptools.sandbox import run_setup

from . import run_cmd


TEST_SETUP_PY = """\
#!/usr/bin/env python
from __future__ import print_function

import os
import sys
for k in list(sys.modules):
    if k == 'astropy_helpers' or k.startswith('astropy_helpers.'):
        del sys.modules[k]

import ah_bootstrap
ah_bootstrap.use_astropy_helpers({args})

import astropy_helpers
print(os.path.abspath(astropy_helpers.__file__))
"""


def test_bootstrap_from_submodule(tmpdir, capsys):
    """
    Tests importing astropy_helpers from a submodule in a git repository.
    This tests actually performing a fresh clone of the repository without
    the submodule initialized, and that importing astropy_helpers in that
    context works transparently after calling
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
        run_cmd('git', ['submodule', 'add', os.path.abspath(old_cwd),
                        'astropy_helpers'])

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
        assert path == str(tmpdir.join('clone', 'astropy_helpers',
                                       'astropy_helpers', '__init__.py'))
    finally:
        os.chdir(old_cwd)
