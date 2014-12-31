astropy-helpers Changelog
=========================

0.4.4 (2014-12-31)
------------------

- More improvements for building the documentation using Python 3.x. [#100]

- Additional minor fixes to Python 3 support. [#115]

- Updates to support new test features in Astropy [#92, #106]


0.4.3 (2014-10-22)
------------------

- The generated ``version.py`` file now preserves the git hash of installed
  copies of the package as well as when building a source distribution.  That
  is, the git hash of the changeset that was installed/released is preserved.
  [#87]

- In smart resolver add resolution for class links when they exist in the
  intersphinx inventory, but not the mapping of the current package
  (e.g. when an affiliated package uses an astropy core class of which
  "actual" and "documented" location differs) [#88]

- Fixed a bug that could occur when running ``setup.py`` for the first time
  in a repository that uses astropy-helpers as a submodule:
  ``AttributeError: 'NoneType' object has no attribute 'mkdtemp'`` [#89]

- Fixed a bug where optional arguments to the ``doctest-skip`` Sphinx
  directive were sometimes being left in the generated documentation output.
  [#90]

- Improved support for building the documentation using Python 3.x. [#96]

- Avoid error message if .git directory is not present. [#91]


0.4.2 (2014-08-09)
------------------

- Fixed some CSS issues in generated API docs. [#69]

- Fixed the warning message that could be displayed when generating a
  version number with some older versions of git. [#77]

- Fixed automodsumm to work with new versions of Sphinx (>= 1.2.2). [#80]


0.4.1 (2014-08-08)
------------------

- Fixed git revision count on systems with git versions older than v1.7.2.
  [#70]

- Fixed display of warning text when running a git command fails (previously
  the output of stderr was not being decoded properly). [#70]

- The ``--offline`` flag to ``setup.py`` understood by ``ah_bootstrap.py``
  now also prevents git from going online to fetch submodule updates. [#67]

- The Sphinx extension for converting issue numbers to links in the changelog
  now supports working on arbitrary pages via a new ``conf.py`` setting:
  ``changelog_links_docpattern``.  By default it affects the ``changelog``
  and ``whatsnew`` pages in one's Sphinx docs. [#61]

- Fixed crash that could result from users with missing/misconfigured
  locale settings. [#58]

- The font used for code examples in the docs is now the
  system-defined ``monospace`` font, rather than ``Minaco``, which is
  not available on all platforms. [#50]


0.4 (2014-07-15)
----------------

- Initial release of astropy-helpers.  See `APE4
  <https://github.com/astropy/astropy-APEs/blob/master/APE4.rst>`_ for
  details of the motivation and design of this package.

- The ``astropy_helpers`` package replaces the following modules in the
  ``astropy`` package:

  - ``astropy.setup_helpers`` -> ``astropy_helpers.setup_helpers``

  - ``astropy.version_helpers`` -> ``astropy_helpers.version_helpers``

  - ``astropy.sphinx`` - > ``astropy_helpers.sphinx``

  These modules should be considered deprecated in ``astropy``, and any new,
  non-critical changes to those modules will be made in ``astropy_helpers``
  instead.  Affiliated packages wishing to make use those modules (as in the
  Astropy package-template) should use the versions from ``astropy_helpers``
  instead, and include the ``ah_bootstrap.py`` script in their project, for
  bootstrapping the ``astropy_helpers`` package in their setup.py script.
