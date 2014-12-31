from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import inspect
import os
import shutil
import subprocess
import sys
import tempfile

from distutils.core import Command

from .compat import _fix_user_options


PY3 = sys.version_info[0] == 3


class AstropyTest(Command, object):
    description = 'Run the tests for this package'

    user_options = [
        ('package=', 'P',
         "The name of a specific package to test, e.g. 'io.fits' or 'utils'.  "
         "If nothing is specified, all default tests are run."),
        ('test-path=', 't',
         'Specify a test location by path.  If a relative path to a  .py file, '
         'it is relative to the built package, so e.g., a  leading "astropy/" '
         'is necessary.  If a relative  path to a .rst file, it is relative to '
         'the directory *below* the --docs-path directory, so a leading '
         '"docs/" is usually necessary.  May also be an absolute path.'),
        ('verbose-results', 'V',
         'Turn on verbose output from pytest.'),
        ('plugins=', 'p',
         'Plugins to enable when running pytest.'),
        ('pastebin=', 'b',
         "Enable pytest pastebin output. Either 'all' or 'failed'."),
        ('args=', 'a',
         'Additional arguments to be passed to pytest.'),
        ('remote-data', 'R', 'Run tests that download remote data.'),
        ('pep8', '8',
         'Enable PEP8 checking and disable regular tests. '
         'Requires the pytest-pep8 plugin.'),
        ('pdb', 'd',
         'Start the interactive Python debugger on errors.'),
        ('coverage', 'c',
         'Create a coverage report. Requires the coverage package.'),
        ('open-files', 'o', 'Fail if any tests leave files open.  Requires the '
         'psutil package.'),
        ('parallel=', 'j',
         'Run the tests in parallel on the specified number of '
         'CPUs.  If negative, all the cores on the machine will be '
         'used.  Requires the pytest-xdist plugin.'),
        ('docs-path=', None,
         'The path to the documentation .rst files.  If not provided, and '
         'the current directory contains a directory called "docs", that '
         'will be used.'),
        ('skip-docs', None,
         "Don't test the documentation .rst files."),
        ('repeat=', None,
         'How many times to repeat each test (can be used to check for '
         'sporadic failures).')
    ]

    user_options = _fix_user_options(user_options)

    package_name = ''

    def initialize_options(self):
        self.package = None
        self.test_path = None
        self.verbose_results = False
        self.plugins = None
        self.pastebin = None
        self.args = None
        self.remote_data = False
        self.pep8 = False
        self.pdb = False
        self.coverage = False
        self.open_files = False
        self.parallel = 0
        self.docs_path = None
        self.skip_docs = False
        self.repeat = None

    def finalize_options(self):
        # Normally we would validate the options here, but that's handled in
        # run_tests
        pass

    def run(self):
        try:
            import astropy
        except ImportError:
            raise ImportError(
                "The 'test' command requires the astropy package to be "
                "installed and importable.")

        self.reinitialize_command('build', inplace=False)
        self.run_command('build')
        build_cmd = self.get_finalized_command('build')
        new_path = os.path.abspath(build_cmd.build_lib)

        if self.docs_path is None:
            if os.path.exists('docs'):
                self.docs_path = os.path.abspath('docs')
        else:
            self.docs_path = os.path.abspath(self.docs_path)

        # Copy the build to a temporary directory for the purposes of testing
        # - this avoids creating pyc and __pycache__ directories inside the
        # build directory
        tmp_dir = tempfile.mkdtemp(prefix=self.package_name + '-test-')
        testing_path = os.path.join(tmp_dir, os.path.basename(new_path))
        shutil.copytree(new_path, testing_path)
        shutil.copy('setup.cfg', testing_path)

        cmd_pre = ''
        cmd_post = ''

        try:
            if self.coverage:
                if self.parallel != 0:
                    raise ValueError(
                        "--coverage can not be used with --parallel")

                try:
                    import coverage
                except ImportError:
                    raise ImportError(
                        "--coverage requires that the coverage package is "
                        "installed.")

                # Don't use get_pkg_data_filename here, because it
                # requires importing astropy.config and thus screwing
                # up coverage results for those packages.
                coveragerc = os.path.join(
                    testing_path, self.package_name, 'tests', 'coveragerc')

                # We create a coveragerc that is specific to the version
                # of Python we're running, so that we can mark branches
                # as being specifically for Python 2 or Python 3
                with open(coveragerc, 'r') as fd:
                    coveragerc_content = fd.read()
                if PY3:
                    ignore_python_version = '2'
                else:
                    ignore_python_version = '3'
                coveragerc_content = coveragerc_content.replace(
                    "{ignore_python_version}", ignore_python_version).replace(
                        "{packagename}", self.package_name)
                tmp_coveragerc = os.path.join(tmp_dir, 'coveragerc')
                with open(tmp_coveragerc, 'wb') as tmp:
                    tmp.write(coveragerc_content.encode('utf-8'))

                cmd_pre = (
                    'import coverage; '
                    'cov = coverage.coverage(data_file="{0}", config_file="{1}"); '
                    'cov.start();'.format(
                        os.path.abspath(".coverage"), tmp_coveragerc))
                cmd_post = (
                    'cov.stop(); '
                    'from astropy.tests.helper import _save_coverage; '
                    '_save_coverage(cov, result, "{0}", "{1}");'.format(
                        os.path.abspath('.'), testing_path))

            test_args = filter(lambda arg: hasattr(self, arg),
                               self._get_test_runner_args())

            test_args = ', '.join('{0}={1!r}'.format(arg, getattr(self, arg))
                                  for arg in test_args)

            if PY3:
                set_flag = "import builtins; builtins._ASTROPY_TEST_ = True"
            else:
                set_flag = "import __builtin__; __builtin__._ASTROPY_TEST_ = True"

            cmd = ('{cmd_pre}{0}; import {1.package_name}, sys; result = '
                   '{1.package_name}.test({test_args}); {cmd_post}'
                   'sys.exit(result)')

            cmd = cmd.format(set_flag, self, cmd_pre=cmd_pre,
                             cmd_post=cmd_post, test_args=test_args)

            # Run the tests in a subprocess--this is necessary since
            # new extension modules may have appeared, and this is the
            # easiest way to set up a new environment

            # Remove temporary directory
            # On Python 3.x prior to 3.3, the creation of .pyc files
            # is not atomic.  py.test jumps through some hoops to make
            # this work by parsing import statements and carefully
            # importing files atomically.  However, it can't detect
            # when __import__ is used, so its carefulness still fails.
            # The solution here (admittedly a bit of a hack), is to
            # turn off the generation of .pyc files altogether by
            # passing the `-B` switch to `python`.  This does mean
            # that each core will have to compile .py file to bytecode
            # itself, rather than getting lucky and borrowing the work
            # already done by another core.  Compilation is an
            # insignificant fraction of total testing time, though, so
            # it's probably not worth worrying about.
            retcode = subprocess.call([sys.executable, '-B', '-c', cmd],
                                      cwd=testing_path, close_fds=False)
        finally:
            shutil.rmtree(tmp_dir)

        raise SystemExit(retcode)

    def _get_test_runner_args(self):
        """
        A hack to determine what arguments are supported by the package's
        test() function.  In the future there should be a more straightforward
        API to determine this (really it should be determined by the
        ``TestRunner`` class for whatever version of Astropy is in use).
        """

        if PY3:
            import builtins
            builtins._ASTROPY_TEST_ = True
        else:
            import __builtin__
            __builtin__._ASTROPY_TEST_ = True

        try:
            pkg = __import__(self.package_name)
            if not hasattr(pkg, 'test'):
                raise ImportError(
                    'package {0} does not have a {0}.test() function as '
                    'required by the Astropy test runner'.format(package_name))

            argspec = inspect.getargspec(pkg.test)
            return argspec.args
        finally:
            if PY3:
                del builtins._ASTROPY_TEST_
            else:
                del __builtin__._ASTROPY_TEST_
