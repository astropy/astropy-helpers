Notes for astropy-helpers contributors
======================================

If you contribute a change to astropy-helpers and want to try it out with a
package that already uses astropy-helpers, install astropy-helpers from your
branch of the repository in editable mode::

    pip install -e .

Then go to your package and add the ``--use-system-astropy-helpers`` for any
``setup.py`` command you want to check, e.g.::

    python setup.py build_docs --use-system-astropy-helpers

This will cause the installed version to be used instead of any local submodule.
