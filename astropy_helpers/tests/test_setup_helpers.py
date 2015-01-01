import shutil
import sys

from textwrap import dedent

from setuptools.sandbox import run_setup

from .. import setup_helpers
from ..setup_helpers import get_package_info, register_commands
from . import *


def test_cython_autoextensions(tmpdir):
    """
    Regression test for https://github.com/astropy/astropy-helpers/pull/19

    Ensures that Cython extensions in sub-packages are discovered and built
    only once.
    """

    # Make a simple test package
    test_pkg = tmpdir.mkdir('test_pkg')
    test_pkg.mkdir('yoda').mkdir('luke')
    test_pkg.ensure('yoda', '__init__.py')
    test_pkg.ensure('yoda', 'luke', '__init__.py')
    test_pkg.join('yoda', 'luke', 'dagobah.pyx').write(
        """def testfunc(): pass""")

    # Required, currently, for get_package_info to work
    register_commands('yoda', '0.0', False, srcdir=str(test_pkg))
    package_info = get_package_info(str(test_pkg))

    assert len(package_info['ext_modules']) == 1
    assert package_info['ext_modules'][0].name == 'yoda.luke.dagobah'


def test_no_cython_buildext(tmpdir):
    """
    Regression test for https://github.com/astropy/astropy-helpers/pull/35

    This tests the custom build_ext command installed by astropy_helpers when
    used with a project that has no Cython extensions (but does have one or
    more normal C extensions).
    """

    # In order for this test to test the correct code path we need to fool
    # setup_helpers into thinking we don't have Cython installed
    setup_helpers._module_state['have_cython'] = False

    test_pkg = tmpdir.mkdir('test_pkg')
    test_pkg.mkdir('_eva_').ensure('__init__.py')

    # TODO: It might be later worth making this particular test package into a
    # reusable fixture for other build_ext tests

    # A minimal C extension for testing
    test_pkg.join('_eva_').join('unit01.c').write(dedent("""\
        #include <Python.h>
        #ifndef PY3K
        #if PY_MAJOR_VERSION >= 3
        #define PY3K 1
        #else
        #define PY3K 0
        #endif
        #endif

        #if PY3K
        static struct PyModuleDef moduledef = {
            PyModuleDef_HEAD_INIT,
            "unit01",
            NULL,
            -1,
            NULL
        };
        PyMODINIT_FUNC
        PyInit_unit01(void) {
            return PyModule_Create(&moduledef);
        }
        #else
        PyMODINIT_FUNC
        initunit01(void) {
            Py_InitModule3("unit01", NULL, NULL);
        }
        #endif
    """))

    test_pkg.join('setup.py').write(dedent("""\
        from os.path import join
        from setuptools import setup, Extension
        from astropy_helpers.setup_helpers import register_commands

        NAME = '_eva_'
        VERSION = 0.1
        RELEASE = True

        cmdclassd = register_commands(NAME, VERSION, RELEASE)

        setup(
            name=NAME,
            version=VERSION,
            cmdclass=cmdclassd,
            ext_modules=[Extension('_eva_.unit01',
                                   [join('_eva_', 'unit01.c')])]
        )
    """))

    with test_pkg.as_cwd():
        run_setup('setup.py', ['build_ext', '--inplace'])

    sys.path.insert(0, str(test_pkg))
    try:
        import _eva_.unit01
        dirname = os.path.abspath(os.path.dirname(_eva_.unit01.__file__))
        assert dirname == str(test_pkg.join('_eva_'))
    finally:
        cleanup_import('_eva_')
        sys.path.remove(str(test_pkg))


@pytest.mark.parametrize('mode', ['cli', 'cli-w', 'direct'])
def test_build_sphinx(tmpdir, mode):
    """
    Test for build_sphinx
    """

    import astropy_helpers
    ah_path = os.path.dirname(astropy_helpers.__file__)

    test_pkg = tmpdir.mkdir('test_pkg')

    test_pkg.mkdir('mypackage')

    test_pkg.join('mypackage').join('__init__.py').write(dedent("""\
        def test_function():
            "Test function"
            pass

        class A():
            "Test class A"
            pass

        class B(A):
            "Test class B"
            pass
    """))

    docs = test_pkg.mkdir('docs')

    autosummary = docs.mkdir('_templates').mkdir('autosummary')

    autosummary.join('base.rst').write('{% extends "autosummary_core/base.rst" %}')
    autosummary.join('class.rst').write('{% extends "autosummary_core/class.rst" %}')
    autosummary.join('module.rst').write('{% extends "autosummary_core/module.rst" %}')

    docs_dir = test_pkg.join('docs')

    docs_dir.join('conf.py').write(dedent("""\
        import sys
        sys.path.append("../")
        import warnings
        with warnings.catch_warnings():  # ignore matplotlib warning
            warnings.simplefilter("ignore")
            from astropy_helpers.sphinx.conf import *
        exclude_patterns.append('_templates')
        require_docstring_on_public_objects = True
    """))

    docs_dir.join('index.rst').write(dedent("""\
        .. automodapi:: mypackage
    """))

    test_pkg.join('setup.py').write(dedent("""\
        from os.path import join
        from setuptools import setup, Extension
        from astropy_helpers.setup_helpers import register_commands, get_package_info

        NAME = 'mypackage'
        VERSION = 0.1
        RELEASE = True

        cmdclassd = register_commands(NAME, VERSION, RELEASE)

        setup(
            name=NAME,
            version=VERSION,
            cmdclass=cmdclassd,
            **get_package_info()
        )
    """))

    with test_pkg.as_cwd():
        shutil.copytree(ah_path, 'astropy_helpers')

        if mode == 'cli':
            run_setup('setup.py', ['build_sphinx'])
        elif mode == 'cli-w':
            run_setup('setup.py', ['build_sphinx', '-w'])
        elif mode == 'direct':  # to check coverage
            with docs_dir.as_cwd():
                from sphinx import main
                try:
                    main(['-b html', '-d _build/doctrees', '.', '_build/html'])
                except SystemExit as exc:
                    assert exc.code == 0


def test_command_hooks(tmpdir, capsys):
    """A basic test for pre- and post-command hooks."""

    test_pkg = tmpdir.mkdir('test_pkg')
    test_pkg.mkdir('_welltall_')
    test_pkg.join('_welltall_', '__init__.py').ensure()

    # Create a setup_package module with a couple of command hooks in it
    test_pkg.join('_welltall_', 'setup_package.py').write(dedent("""\
        def pre_build_hook(cmd_obj):
            print('Hello build!')

        def post_build_hook(cmd_obj):
            print('Goodbye build!')

    """))

    # A simple setup.py for the test package--running register_commands should
    # discover and enable the command hooks
    test_pkg.join('setup.py').write(dedent("""\
        from os.path import join
        from setuptools import setup, Extension
        from astropy_helpers.setup_helpers import register_commands, get_package_info

        NAME = '_welltall_'
        VERSION = 0.1
        RELEASE = True

        cmdclassd = register_commands(NAME, VERSION, RELEASE)

        setup(
            name=NAME,
            version=VERSION,
            cmdclass=cmdclassd
        )
    """))

    with test_pkg.as_cwd():
        try:
            run_setup('setup.py', ['build'])
        finally:
            cleanup_import('_welltall_')

    stdout, stderr = capsys.readouterr()
    want = dedent("""\
        running build
        running pre_hook from _welltall_.setup_package for build command
        Hello build!
        running post_hook from _welltall_.setup_package for build command
        Goodbye build!
    """).strip()

    assert want in stdout
