# Versioning info following PEP440 with added requirement of mandatory
#  micro version.
__version_info__ = (0, 8, 2)
__version__ = '.'.join(map(str, __version_info__))

__all__ = ['client']

from . import client
