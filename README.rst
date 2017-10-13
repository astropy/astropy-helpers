astropy-helpers
===============

* Stable versions: https://pypi.org/project/astropy-helpers/
* Development version, issue tracker: https://github.com/astropy/astropy-helpers

This project provides a Python package, ``astropy_helpers``, which includes
many build, installation, and documentation-related tools used by the Astropy
project, but packaged separately for use by other projects that wish to
leverage this work.  The motivation behind this package and details of its
implementation are in the accepted 
`Astropy Proposal for Enhancement (APE) 4 <https://github.com/astropy/astropy-APEs/blob/master/APE4.rst>`_.

The ``astropy_helpers.extern`` sub-module includes modules developed elsewhere
that are bundled here for convenience. At the moment, this consists of the
following two sphinx extensions:

* `numpydoc <https://github.com/numpy/numpydoc>`_, a Sphinx extension
  developed as part of the Numpy project. This is used to parse docstrings
  in Numpy format

* `sphinx-automodapi <https://github.com/astropy/sphinx-automodapi>`_, a Sphinx
  extension developed as part of the Astropy project. This used to be developed
  directly in ``astropy-helpers`` but is now a standalone package.

Issues with these sub-modules should be reported in their respective repositories,
and we will regularly update the bundled versions to reflect the latest released
versions.

``astropy_helpers`` includes a special "bootstrap" module called
``ah_bootstrap.py`` which is intended to be used by a project's setup.py in
order to ensure that the ``astropy_helpers`` package is available for
build/installation.  This is similar to the ``ez_setup.py`` module that is
shipped with some projects to bootstrap `setuptools
<https://bitbucket.org/pypa/setuptools>`_.

As described in APE4, the version numbers for ``astropy_helpers`` follow the
corresponding major/minor version of the `astropy core package
<http://www.astropy.org/>`_, but with an independent sequence of micro (bugfix)
version numbers. Hence, the initial release is 0.4, in parallel with Astropy
v0.4, which will be the first version  of Astropy to use ``astropy-helpers``.

For examples of how to implement ``astropy-helpers`` in a project,
see the ``setup.py`` and ``setup.cfg`` files of the 
`Affiliated package template <https://github.com/astropy/package-template>`_.

.. image:: https://travis-ci.org/astropy/astropy-helpers.svg
    :target: https://travis-ci.org/astropy/astropy-helpers

.. image:: https://coveralls.io/repos/astropy/astropy-helpers/badge.svg
    :target: https://coveralls.io/r/astropy/astropy-helpers
