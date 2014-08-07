# Licensed under a 3-clause BSD style license - see LICENSE.rst

"""
Utilities for retrieving revision information from a project's git repository.
"""

# Do not remove the following comment; it is used by
# astropy_helpers.version_helpers to determine the beginning of the code in
# this module

# BEGIN


import os
import re
import sys
import subprocess as sp
import warnings


if sys.version_info[0] < 3:
    _text_type = unicode
else:
    _text_type = str


_git_version_re = re.compile(r'(?:\d\.){1,3}\d')


class _CommandNotFound(OSError):
    """
    An exception raised when a command run with run_git is not found on the
    system.
    """


# Note: The reason this isn't a generic utility is that it also needs to be
# copied into the project's version.py module, so it will remain git-specific
def run_git(cmd, cwd=None):
    """
    Run a git command in a subprocess, given as a list of command-line
    arguments.

    Returns a ``(returncode, stdout, stderr)`` tuple.
    """

    cmd = ['git'] + cmd

    try:
        p = sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.PIPE, cwd=cwd)
        # XXX: May block if either stdout or stderr fill their buffers;
        # however for the commands this is currently used for that is
        # unlikely (they should have very brief output)
        stdout, stderr = p.communicate()
    except OSError as e:
        if e.errno == errno.ENOENT:
            msg = 'Command not found: `{0}`'.format(' '.join(cmd))
            raise _CommandNotFound(msg, cmd)
        else:
            raise

    # The commands we're using this for should really only be returning ASCII
    # But if any non-ASCII output comes out we don't care about it
    if not isinstance(stdout, _text_type):
        stdout = stdout.decode('latin1')
    if not isinstance(stderr, _text_type):
        stderr = stderr.decode('latin1')

    return (p.returncode, stdout, stderr)


def update_git_devstr(version, path=None):
    """
    Updates the git revision string if and only if the path is being imported
    directly from a git working copy.  This ensures that the revision number in
    the version string is accurate.
    """

    try:
        # Quick way to determine if we're in git or not - returns '' if not
        devstr = get_git_devstr(sha=True, show_warning=False, path=path)
    except OSError:
        return version

    if not devstr:
        # Probably not in git so just pass silently
        return version

    if 'dev' in version:  # update to the current git revision
        version_base = version.split('.dev', 1)[0]
        devstr = get_git_devstr(sha=False, show_warning=False, path=path)

        return version_base + '.dev' + devstr
    else:
        #otherwise it's already the true/release version
        return version


_git_version = ()
def get_git_version():
    global _git_version

    if _git_version:
        return _git_version

    version = ()

    try:
        returncode, stdout, _ = run_git(['--version'])
    except:
        # Ignore exceptions and just assume we can't get a version for git
        pass
    else:
        m = _git_version_re.search(stdout)
        if m:
            version = tuple(int(part) for part in m.group(0).split('.'))

    _git_version = version
    return version


def get_git_devstr(sha=False, show_warning=True, path=None):
    """
    Determines the number of revisions in this repository.

    Parameters
    ----------
    sha : bool
        If True, the full SHA1 hash will be returned. Otherwise, the total
        count of commits in the repository will be used as a "revision
        number".

    show_warning : bool
        If True, issue a warning if git returns an error code, otherwise errors
        pass silently.

    path : str or None
        If a string, specifies the directory to look in to find the git
        repository.  If `None`, the current working directory is used.
        If given a filename it uses the directory containing that file.

    Returns
    -------
    devversion : str
        Either a string with the revsion number (if `sha` is False), the
        SHA1 hash of the current commit (if `sha` is True), or an empty string
        if git version info could not be identified.

    """

    if path is None:
        path = os.getcwd()

    if not os.path.isdir(path):
        path = os.path.abspath(os.path.dirname(path))

    if not os.path.exists(os.path.join(path, '.git')):
        return ''

    # git rev-list didn't support the --count argument before v1.7.2
    can_count = get_git_version()[:3] >= (1, 7, 2)

    if sha:
        # Faster for getting just the hash of HEAD
        cmd = ['rev-parse', 'HEAD']
    elif can_count:
        cmd = ['rev-list', '--count', 'HEAD']
    else:
        cmd = ['rev-list', 'HEAD']

    try:
        returncode, stdout, stderr = run_git(cmd, cwd=path)
    except _CommandNotFound:
        if show_warning:
            warnings.warn('Error running git: git command not found')
    except OSError as e:
        if show_warning:
            warnings.warn('Error running git: ' + str(e))
        return ''

    if returncode == 128:
        if show_warning:
            warnings.warn('No git repository present at {0!r}! Using default '
                          'dev version.'.format(path))
        return ''
    elif returncode != 0:
        if show_warning:
            warnings.warn('Git failed while determining revision '
                          'count: ' + stderr)
        return ''

    if sha:
        return stdout[:40]
    elif can_count:
        return stdout.strip()
    else:
        return str(stdout.count('\n'))
