Updating extension-helpers in a package
=====================================

Automatic update
----------------

If you would like the Astropy team to automatically open pull requests to update
extension-helpers in your package, then see the instructions `here
<https://github.com/astropy/astropy-procedures/blob/master/update-packages/README.md>`_.

Manual update
-------------

To instead update extension-helpers manually, go inside the submodule and do::

    cd extension_helpers
    git fetch origin

Then checkout the version you want to use, e.g.::

    git checkout v3.0.3

Go back up to the root of the repository and update the ``ah_bootstap.py`` file
too, then add your changes::

    cp extension_helpers/ah_bootstrap.py .
    git add extension_helpers ah_bootstrap.py
    git commit ...
