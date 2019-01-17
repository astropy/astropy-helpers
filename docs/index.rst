astropy-helpers documentation
=============================

About
-----

The **astropy-helpers** package includes
many build, installation, and documentation-related tools used by the Astropy
project, but packaged separately for use by other projects that wish to
leverage this work. The motivation behind this package and details of its
implementation are in the accepted
`Astropy Proposal for Enhancement (APE) 4 <https://github.com/astropy/astropy-APEs/blob/master/APE4.rst>`_.

As described in `APE4 <https://github.com/astropy/astropy-APEs/blob/master/APE4.rst>`_, the version
numbers for astropy-helpers follow the corresponding major/minor version of
the `astropy core package <http://www.astropy.org/>`_, but with an independent
sequence of micro (bugfix) version numbers. Hence, the initial release is 0.4,
in parallel with Astropy v0.4, which will be the first version  of Astropy to
use astropy-helpers.

For a real-life example of how to implement astropy-helpers in a project,
see the ``setup.py`` and ``setup.cfg`` files of the
`Affiliated package template <https://github.com/astropy/package-template>`_.

Please note that version v3.0 and later of astropy-helpers
requires Python 3.5 or later. If you wish to maintain Python 2 support
for your package that uses astropy-helpers, then do not upgrade the
helpers to v3.0 or later. We will still provide Python 2.7 compatible
v2.0.x releases until the end of 2019.

User/developer guide
--------------------
.. toctree::
   :maxdepth: 2

   basic.rst
   advanced.rst
   using.rst
   updating.rst
   known_issues.rst
   developers.rst
   api.rst
