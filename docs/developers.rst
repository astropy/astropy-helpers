Notes for extension-helpers contributors
======================================

Note about versions
-------------------

As described in `APE4
<https://github.com/astropy/astropy-APEs/blob/master/APE4.rst>`_, the version
numbers for extension-helpers follow the corresponding major/minor version of the
`astropy core package <http://www.astropy.org/>`_, but with an independent
sequence of micro (bugfix) version numbers. Hence, the initial release is 0.4,
in parallel with Astropy v0.4, which will be the first version  of Astropy to
use extension-helpers.

Trying out changes
------------------

If you contribute a change to extension-helpers and want to try it out with a
package that already uses extension-helpers, install extension-helpers from your
branch of the repository in editable mode::

    pip install -e .

Then go to your package and add the ``--use-system-extension-helpers`` for any
``setup.py`` command you want to check, e.g.::

    python setup.py build_docs --use-system-extension-helpers

This will cause the installed version to be used instead of any local submodule.
