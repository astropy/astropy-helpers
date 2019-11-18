
import os
import pkgutil
import re
import shutil
import subprocess
import sys
from distutils.version import LooseVersion

from distutils import log

from sphinx.setup_command import BuildDoc as SphinxBuildDoc

SUBPROCESS_TEMPLATE = """
import os
import sys

{build_main}

os.chdir({srcdir!r})

{sys_path_inserts}

for builder in {builders!r}:
    retcode = build_main(argv={argv!r} + ['-b', builder, '.', os.path.join({output_dir!r}, builder)])
    if retcode != 0:
        sys.exit(retcode)
"""


def ensure_sphinx_astropy_installed():
    """
    Make sure that sphinx-astropy is available.
    """

    try:
        from sphinx_astropy import __version__ as sphinx_astropy_version  # noqa
    except ImportError:
        sphinx_astropy_version = None

    if (sphinx_astropy_version is None
            or LooseVersion(sphinx_astropy_version) < LooseVersion('1.2')):
        raise ImportError("sphinx-astropy 1.2 or later needs to be installed to build "
                            "the documentation.")


class AstropyBuildDocs(SphinxBuildDoc):
    """
    A version of the ``build_docs`` command that uses the version of Astropy
    that is built by the setup ``build`` command, rather than whatever is
    installed on the system.  To build docs against the installed version, run
    ``make html`` in the ``astropy/docs`` directory.
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
    user_options.append(
        ('parallel=', 'j',
         'Build the docs in parallel on the specified number of '
         'processes. If "auto", all the cores on the machine will be '
         'used.'))

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
        self.traceback = False
        self.parallel = None

    def finalize_options(self):

        # This has to happen before we call the parent class's finalize_options
        if self.build_dir is None:
            self.build_dir = 'docs/_build'

        SphinxBuildDoc.finalize_options(self)

        # Clear out previous sphinx builds, if requested
        if self.clean_docs:

            dirstorm = [os.path.join(self.source_dir, 'api'),
                        os.path.join(self.source_dir, 'generated')]

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

        build_main = 'from sphinx.cmd.build import build_main'

        # We need to make sure sphinx-astropy is installed
        ensure_sphinx_astropy_installed()

        sys_path_inserts = [build_cmd_path, ah_path]
        sys_path_inserts = os.linesep.join(['sys.path.insert(0, {0!r})'.format(path) for path in sys_path_inserts])

        argv = []

        if self.warnings_returncode:
            argv.append('-W')

        if self.no_intersphinx:
            argv.extend(['-D', 'disable_intersphinx=1'])

        # We now need to adjust the flags based on the parent class's options

        if self.fresh_env:
            argv.append('-E')

        if self.all_files:
            argv.append('-a')

        if getattr(self, 'pdb', False):
            argv.append('-P')

        if getattr(self, 'nitpicky', False):
            argv.append('-n')

        if self.traceback:
            argv.append('-T')

        # The default verbosity level is 1, so in that case we just don't add a flag
        if self.verbose == 0:
            argv.append('-q')
        elif self.verbose > 1:
            argv.append('-v')

        if self.parallel is not None:
            argv.append(f'-j={self.parallel}')

        if isinstance(self.builder, str):
            builders = [self.builder]
        else:
            builders = self.builder

        subproccode = SUBPROCESS_TEMPLATE.format(build_main=build_main,
                                                 srcdir=self.source_dir,
                                                 sys_path_inserts=sys_path_inserts,
                                                 builders=builders,
                                                 argv=argv,
                                                 output_dir=os.path.abspath(self.build_dir))

        log.debug('Starting subprocess of {0} with python code:\n{1}\n'
                  '[CODE END])'.format(sys.executable, subproccode))

        proc = subprocess.Popen([sys.executable], stdin=subprocess.PIPE)
        proc.communicate(subproccode.encode('utf-8'))
        if proc.returncode != 0:
            retcode = proc.returncode

        if retcode is None:
            if self.open_docs_in_browser:
                if self.builder == 'html':
                    absdir = os.path.abspath(self.builder_target_dir)
                    index_path = os.path.join(absdir, 'index.html')
                    fileurl = 'file://' + pathname2url(index_path)
                    webbrowser.open(fileurl)
                else:
                    log.warn('open-docs-in-browser option was given, but '
                             'the builder is not html! Ignoring.')

        # Here we explicitly check proc.returncode since we only want to output
        # this for cases where the return code really wasn't 0.
        if proc.returncode:
            log.warn('Sphinx Documentation subprocess failed with return '
                     'code ' + str(proc.returncode))

        if retcode is not None:
            # this is potentially dangerous in that there might be something
            # after the call to `setup` in `setup.py`, and exiting here will
            # prevent that from running.  But there's no other apparent way
            # to signal what the return code should be.
            sys.exit(retcode)


class AstropyBuildSphinx(AstropyBuildDocs):  # pragma: no cover
    def run(self):
        AstropyBuildDocs.run(self)
