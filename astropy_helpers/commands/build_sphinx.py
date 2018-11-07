from __future__ import print_function

import os
import pkgutil
import re
import shutil
import subprocess
import sys
import glob
import textwrap
import warnings

from distutils import log

from sphinx.setup_command import BuildDoc as SphinxBuildDoc

from ..utils import AstropyDeprecationWarning


class AstropyBuildDocs(SphinxBuildDoc):
    """
    A version of the ``build_docs`` command that uses the version of Astropy
    that is built by the setup ``build`` command, rather than whatever is
    installed on the system.  To build docs against the installed version, run
    ``make html`` in the ``astropy/docs`` directory.

    This also automatically creates the docs/_static directories--this is
    needed because GitHub won't create the _static dir because it has no
    tracked files.
    """

    description = 'Build Sphinx documentation for Astropy environment'
    user_options = SphinxBuildDoc.user_options[:]
    user_options.append(
        ('warnings-returncode', 'w',
         'Parses the sphinx output and sets the return code to 1 if there '
         'are any warnings. Note that this will cause the sphinx log to '
         'only update when it completes, rather than continuously as is '
         'normally the case.'))
    user_options.append(
        ('clean-docs', 'l',
         'Completely clean previous builds, including '
         'automodapi-generated files before building new ones'))
    user_options.append(
        ('no-intersphinx', 'n',
         'Skip intersphinx, even if conf.py says to use it'))
    user_options.append(
        ('open-docs-in-browser', 'o',
         'Open the docs in a browser (using the webbrowser module) if the '
         'build finishes successfully.'))

    boolean_options = SphinxBuildDoc.boolean_options[:]
    boolean_options.append('warnings-returncode')
    boolean_options.append('clean-docs')
    boolean_options.append('no-intersphinx')
    boolean_options.append('open-docs-in-browser')

    _self_iden_rex = re.compile(r"self\.([^\d\W][\w]+)", re.UNICODE)

    def initialize_options(self):
        SphinxBuildDoc.initialize_options(self)
        self.clean_docs = False
        self.no_intersphinx = False
        self.open_docs_in_browser = False
        self.warnings_returncode = False

    def finalize_options(self):

        SphinxBuildDoc.finalize_options(self)

        # Clear out previous sphinx builds, if requested
        if self.clean_docs:

            dirstorm = [os.path.join(self.source_dir, 'api'),
                        os.path.join(self.source_dir, 'generated')]

            if self.build_dir is None:
                self.build_dir = 'docs/_build'

            dirstorm.append(self.build_dir)

            for d in dirstorm:
                if os.path.isdir(d):
                    log.info('Cleaning directory ' + d)
                    shutil.rmtree(d)
                else:
                    log.info('Not cleaning directory ' + d + ' because '
                             'not present or not a directory')

    def run(self):

        # TODO: Break this method up into a few more subroutines and
        # document them better
        import webbrowser

        from urllib.request import pathname2url

        # This is used at the very end of `run` to decide if sys.exit should
        # be called. If it's None, it won't be.
        retcode = None

        # Now make sure Astropy is built and determine where it was built
        build_cmd = self.reinitialize_command('build')
        build_cmd.inplace = 0
        self.run_command('build')
        build_cmd = self.get_finalized_command('build')
        build_cmd_path = os.path.abspath(build_cmd.build_lib)

        ah_importer = pkgutil.get_importer('astropy_helpers')
        if ah_importer is None:
            ah_path = '.'
        else:
            ah_path = os.path.abspath(ah_importer.path)

        subproccode = textwrap.dedent("""
            import os
            import sys
            from distutils.version import LooseVersion
            from sphinx import __version__

            SPHINX_LT_17 = LooseVersion(__version__) < LooseVersion('1.7')

            if SPHINX_LT_17:
                from sphinx import build_main
            else:
                from sphinx.cmd.build import build_main

            os.chdir({srcdir!r})
            sys.path.insert(0, {build_cmd_path!r})
            sys.path.insert(0, {ah_path!r})
        """).format(build_cmd_path=build_cmd_path, ah_path=ah_path,
                    srcdir=self.source_dir)

        # We've split out the Sphinx part of astropy-helpers into sphinx-astropy
        # but we want it to be auto-installed seamlessly for anyone using
        # build_docs. We check if it's already installed, and if not, we install
        # it to a local .eggs directory and add the eggs to the path (these
        # have to each be added to the path, we can't add them by simply adding
        # .eggs to the path)
        try:
            import sphinx_astropy  # noqa
        except ImportError:
            from setuptools import Distribution
            dist = Distribution()
            dist.fetch_build_eggs('sphinx-astropy')
            eggs_path = os.path.abspath('.eggs')
            # Note that we use append below because we want to make sure that if
            # a user runs a build which populates the .eggs directory, *then*
            # installs sphinx-astropy at the system-level, we want to make sure
            # the .eggs are only used as a last resort if they build the docs
            # again.
            for egg in glob.glob(os.path.join(eggs_path, '*.egg')):
                subproccode += 'sys.path.append({egg!r})\n'.format(egg=egg)

        subproccode += textwrap.dedent("""

            if SPHINX_LT_17:
                argv.insert(0, 'sphinx-build')

            for builder in {builders!r}:
                argv = ['-W', '.', '-b', builder, os.path.join({output_dir!r}, builder)]
                build_main(argv=argv)
        """.format(builders=self.builder,
                   output_dir=os.path.relpath(self.build_dir, 'docs')))

        log.debug('Starting subprocess of {0} with python code:\n{1}\n'
                  '[CODE END])'.format(sys.executable, subproccode))

        # To return the number of warnings, we need to capture stdout. This
        # prevents a continuous updating at the terminal, but there's no
        # apparent way around this.
        if self.warnings_returncode:
            proc = subprocess.Popen([sys.executable, '-c', subproccode],
                                    stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)

            retcode = 1
            with proc.stdout:
                for line in iter(proc.stdout.readline, b''):
                    line = line.strip(b'\r\n')
                    print(line.decode('utf-8'))
                    if 'build succeeded.' == line.decode('utf-8'):
                        retcode = 0

            # Poll to set proc.retcode
            proc.wait()

            if retcode != 0:
                if os.environ.get('TRAVIS', None) == 'true':
                    # this means we are in the travis build, so customize
                    # the message appropriately.
                    msg = ('The build_docs travis build FAILED '
                           'because sphinx issued documentation '
                           'warnings (scroll up to see the warnings).')
                else:  # standard failure message
                    msg = ('build_docs returning a non-zero exit '
                           'code because sphinx issued documentation '
                           'warnings.')
                log.warn(msg)

        else:
            proc = subprocess.Popen([sys.executable], stdin=subprocess.PIPE)
            proc.communicate(subproccode.encode('utf-8'))

        if proc.returncode == 0:
            if self.open_docs_in_browser:
                if self.builder == 'html':
                    absdir = os.path.abspath(self.builder_target_dir)
                    index_path = os.path.join(absdir, 'index.html')
                    fileurl = 'file://' + pathname2url(index_path)
                    webbrowser.open(fileurl)
                else:
                    log.warn('open-docs-in-browser option was given, but '
                             'the builder is not html! Ignoring.')
        else:
            log.warn('Sphinx Documentation subprocess failed with return '
                     'code ' + str(proc.returncode))
            retcode = proc.returncode

        if retcode is not None:
            # this is potentially dangerous in that there might be something
            # after the call to `setup` in `setup.py`, and exiting here will
            # prevent that from running.  But there's no other apparent way
            # to signal what the return code should be.
            sys.exit(retcode)


class AstropyBuildSphinx(AstropyBuildDocs): # pragma: no cover
    description = 'deprecated alias to the build_docs command'

    def run(self):
        warnings.warn(
            'The "build_sphinx" command is now deprecated. Use'
            '"build_docs" instead.', AstropyDeprecationWarning)
        AstropyBuildDocs.run(self)
