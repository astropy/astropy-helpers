Known issues
============

.. warning::
    Note that astropy-helpers is deprecated. As justified and described in `APE17
    <https://github.com/astropy/astropy-APEs/blob/main/APE17.rst>`_, the astropy-helpers
    infrastructure is no longer used for Astropy coordinated or infrastructure packages,
    and hence is no longer maintained.

If you are building a package with a C extension on old MacOS X systems (e.g.
MacOS X 10.7 Lion) you may run into issues (e.g. segmentation fault) with the
default GCC 4.2 compiler available on those systems. If this is the case, you
can tell setuptools to use the clang compiler (which should work) using e.g.::

    CC=clang python setup.py build

See `astropy/astropy#31 <https://github.com/astropy/astropy/issues/31>`_ for a
discussion of the original problem.
