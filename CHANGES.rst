astropy-helpers Changelog
=========================

0.4.2 (unreleased)
------------------

- Fixed automodsumm to work with new versions of Sphinx (>= 1.2.2). [#80]


0.4.1 (2014-08-06)
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
