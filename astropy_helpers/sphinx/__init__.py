"""
This package contains utilities and extensions for the Astropy sphinx
documentation.  In particular, the `astropy.sphinx.conf` should be imported by
the sphinx ``conf.py`` file for affiliated packages that wish to make use of
the Astropy documentation format. Note that some sphinx extensions which are
bundled as-is (numpydoc and sphinx-automodapi) are included in
astropy_helpers.extern rather than astropy_helpers.sphinx.ext.
"""

import os


def get_html_theme_path():
    """Return list of HTML theme paths."""
    cur_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'themes')
    return [cur_dir]
