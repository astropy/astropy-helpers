try:
    from .version import version as __version__
    from .version import githash as __githash__
except ImportError:
    __version__ = ''
    __githash__ = ''


import os
import sys

# Ensure that all module-level code in astropy or other packages know that
# we're in setup mode:
if ('__main__' in sys.modules and
        hasattr(sys.modules['__main__'], '__file__')):
    filename = os.path.basename(sys.modules['__main__'].__file__)

    if filename.rstrip('co') == 'setup.py':
        import builtins
        builtins._ASTROPY_SETUP_ = True

    del filename
