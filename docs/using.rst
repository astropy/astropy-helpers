Using extension-helpers in a package
====================================

To use extension-helpers in your package, you will need to make sure your package
uses a ``pyproject.toml`` file as described in `PEP 518 <https://www.python.org/dev/peps/pep-0518/>`_.

First make sure you follow the instructions in :doc:`basic`, then add
``extension-helpers`` to the build-time dependencies in your ``pyproject.toml`` file::

    [build-system]
    requires = ["setuptools", "wheel", "extension-helpers"]

If you have Cython extensions, you will need to make sure ``cython`` is included in the
above list too.
