About
-----

The **extension-helpers** package includes convenience helpers to assist with
building Python packages with compiled C/Cython extensions.

extension-helpers is not a traditional package in the sense that it
is not intended to be installed directly by users or developers. Instead, it
is meant to be accessed when the ``setup.py`` command is run and should be
defined as a build-time dependency in ``pyproject.toml`` files - see :doc:`using`
for how to do this.

User/developer guide
--------------------
.. toctree::
   :maxdepth: 1

   basic.rst
   advanced.rst
   using.rst
   known_issues.rst
   api.rst
