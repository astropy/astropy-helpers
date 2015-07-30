"""
Different implementations of the ``./setup.py test`` command depending on
what's locally available.

If Astropy v1.1.0.dev or later is available it should be possible to import
AstropyTest from ``astropy.tests.command``.  If ``astropy`` can be imported
but not ``astropy.tests.command`` (i.e. an older version of Astropy), we can
use the backwards-compat implementation of the command.

If Astropy can't be imported at all then there is a skeleton implementation
that allows users to at least discover the ``./setup.py test`` command and
learn that they need Astropy to run it.
"""

try:
    import astropy
    try:
        from astropy.tests.command import AstropyTest
    except ImportError:
        from ._test_compat import AstropyTest
except ImportError:
    # No astropy at all--provide the dummy implementation
    import sys
    from setuptools import Command
    from distutils.errors import DistutilsArgError
    from textwrap import dedent


    class _AstropyTestMeta(type):
        """
        Causes an exception to be raised on accessing user_options so that
        if ``./setup.py test`` is run with additional command-line options we
        can provide a useful error message instead of the default that tells
        users the options are unrecognized.
        """

        @property
        def user_options(cls):
            raise DistutilsArgError(
                "Test 'test' command requires the astropy package to be "
                "installed and importable.")

    if sys.version_info[0] < 3:
        exec(dedent("""
            class _AstropyTestBase(Command, object):
                __metaclass__ = _AstropyTestMeta
        """))
    else:
        exec(dedent("""
            class _AstropyTestBase(Command, metaclass=_AstropyTestMeta):
                pass
        """))

    class AstropyTest(_AstropyTestBase):
        description = 'Run the tests for this package'
