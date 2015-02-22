astropy-helpers
===============

About
-----

This project provides a Python package, ``astropy_helpers``, which includes
many build, installation, and documentation-related tools used by the Astropy
project, but packaged separately for use by other projects that wish to
leverage this work.  The motivation behind this package and details of its
implementation are in the accepted 
`Astropy Proposal for Enhancement (APE) 4 <https://github.com/astropy/astropy-APEs/blob/master/APE4.rst>`_.

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

Getting started
---------------

Note that the ``astropy-helpers`` is not intended to be installed as a normal package. There are several ways to make use of it, which are described below.

As a submodule
^^^^^^^^^^^^^^

The `Affiliated package template <https://github.com/astropy/package-template>`_ provides a complete example of how to include the astropy-helpers module as a submodule.

From PyPI
^^^^^^^^^

In some simpler cases, you may only want to make use of ``astropy-helpers``
within the scope of a single script - for example you may want to use the
Sphinx extensions in ``astropy-helpers`` within a Sphinx ``conf.py`` file. In
this case, you can simply add the following two lines at the top of your
script::

    from setuptools import Distribution
    Distribution({'setup_requires': 'astropy-helpers'})
    
This will download the ``astropy-helpers`` package from PyPI on-the-fly and
include it in a hidden ``.eggs`` directory, and the ``astropy-helpers`` module
can then be imported anywhere in the remainder of the script.

.. image:: https://travis-ci.org/astropy/astropy-helpers.png
    :target: https://travis-ci.org/astropy/astropy-helpers

.. image:: https://coveralls.io/repos/astropy/astropy-helpers/badge.png
    :target: https://coveralls.io/r/astropy/astropy-helpers
