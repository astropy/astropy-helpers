from ..setup_helpers import get_package_info


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

    package_info = get_package_info(str(test_pkg))

    assert len(package_info['ext_modules']) == 1
    assert package_info['ext_modules'][0].name == 'yoda.luke.dagobah'
