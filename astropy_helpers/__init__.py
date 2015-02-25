try:
    from .version import version as __version__
    from .version import githash as __githash__
except ImportError:
    __version__ = ''
    __githash__ = ''


# If we've made it as far as importing astropy_helpers, we don't need
# ah_bootstrap in sys.modules anymore.  Getting rid of it is actually necessary
# if the package we're installing has a setup_requires of another package that
# uses astropy_helpers (and possibly a different version at that)
# See https://github.com/astropy/astropy/issues/3541
import sys
if 'ah_bootstrap' in sys.modules:
    del sys.modules['ah_bootstrap']
