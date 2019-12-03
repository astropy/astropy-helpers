extension-helpers
=================

.. image:: https://travis-ci.org/astropy/extension-helpers.svg
  :target: https://travis-ci.org/astropy/extension-helpers

.. image:: https://ci.appveyor.com/api/projects/status/rt9161t9mhx02xp7/branch/master?svg=true
  :target: https://ci.appveyor.com/project/Astropy/extension-helpers

.. image:: https://codecov.io/gh/astropy/extension-helpers/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/astropy/extension-helpers

The **extension-helpers** package includes many build, installation, and
documentation-related tools used by the Astropy project, but packaged separately
for use by other projects that wish to leverage this work. The motivation behind
this package and details of its implementation are in the accepted
`Astropy Proposal for Enhancement (APE) 4 <https://github.com/astropy/astropy-APEs/blob/master/APE4.rst>`_.

extension-helpers is not a traditional package in the sense that it is not
intended to be installed directly by users or developers. Instead, it is meant
to be accessed when the ``setup.py`` command is run - see the
"`Using extension-helpers in a package <https://extension-helpers.readthedocs.io/en/stable/using.html>`_"
section in the documentation for how to do this.
For a real-life example of how to implement extension-helpers in a
project, see the ``setup.py`` and ``setup.cfg`` files of the
`Affiliated package template <https://github.com/astropy/package-template>`_.

For more information, see the documentation at http://extension-helpers.readthedocs.io
