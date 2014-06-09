astropy-helpers
===============

This project provides a Python package, ``astropy_helpers``, which includes
many build, installation, and documentation-related tools used by the Astropy
project, but packaged separately for use by other projects that wish to
leverage this work.  There is a draft Astropy Proposal for Enhancement dubbed
`APE 4 <https://github.com/embray/astropy-APEs/blob/astropy-helpers/APE4.rst>`_
describing the motivation behind this package and details of its
implementation.  Acceptance of APE 4 is pending only on hammering out minor
details prior to the release of Astropy v0.4.

This also includes a special "bootstrap" module called ``ah_bootstrap.py``
which is intended to be used by a project's setup.py in order to ensure that
the ``astropy_helpers`` package is available for build/installation.  This is
similar to the ``ez_setup.py`` module that is shipped with some projects to
bootstrap `setuptools <https://bitbucket.org/pypa/setuptools>`_.

This preview release of astropy-helpers is intended for testing installation
via PyPI prior to the final initial release which will be astropy-helpers v0.4.
The version of the initial release was chosen, in this case, to parallel
Astropy v0.4, which will be the first version of Astropy to use
astropy-helpers.  As described in APE 4, the major/minor version of
astropy-helpers will be kept parallel with the latest version of Astropy,
though the micro (bugfix) version will be allowed to diverge.

More details will be added to this README before astropy-helpers v0.4 final
is released.  In the meantime, see the setup.py and setup.cfg files in the
`Affiliated package template <https://github.com/astropy/package-template>`_
for examples of its usage.
