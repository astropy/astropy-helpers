Defining extensions
===================

The main functionality in extension-helpers is the
:func:`~extension_helpers.setup_helpers.get_extensions` function which can be
used to collect package extensions. Defining functions is then done in two ways:

* For simple Cython extensions, :func:`~extension_helpers.setup_helpers.get_extensions`
  will automatically generate extension modules with no further work.

* For other extensions, you can create ``setup_package.py`` files anywhere
  in your package, and these files can then include a ``get_extensions``
  function that returns a list of ``distutils.core.Extension`` objects.

In the second case, the idea is that for large packages, extensions can be defined
in the relevant sub-packages rather than having to all be listed in the main
``setup.py`` file. For packages with only a couple of extensions, using
extension-helpers is not really necessary since you can just define these directly
in ``setup.py``.

To use this, you should modify your ``setup.py`` file to use
:func:`~extension_helpers.setup_helpers.get_extensions`  as follows::

    from extension_helpers.setup_helpers import get_extensions
    ...
    setup(..., ext_modules=get_extensions())

Note that if you use this, extension-helpers will also we create a
``packagename.compiler_version`` submodule that contain information about the
compilers used.
