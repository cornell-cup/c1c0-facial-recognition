import sys, os, logging

from typing import List, Tuple

# Computer architecture config.
DEFAULT_PATH: str       = os.getenv('DEFAULT_PATH', 'resources/people')
DEFAULT_OPEN: bool      = os.getenv('DEFAULT_OPEN', True)
DEFAULT_LOAD: bool      = os.getenv('DEFAULT_LOAD', True)
DEFAULT_CACHE: bool     = os.getenv('DEFAULT_CACHE', True)
DEFAULT_CACHE_DIR: str  = os.getenv('DEFAULT_CACHE_DIR', '.cache')
DEFAULT_CAMERA: int     = os.getenv('DEFAULT_CAMERA', None)

# Facial recognition config.
COLORS: List[Tuple[int, int, int]] = [(0, 0, 255), (0, 255, 0), (255, 0, 0), (255, 255, 0), (0, 255, 255)]
DEFAULT_SCALE_FACTOR: float        = 1.0
DEFAULT_NUM_JITTERS: int           = 4
DEFAULT_NUM_UPSAMPLE: int          = 2
DEFAULT_ENCODING_MODEL: str        = 'large'
DEFAULT_NN_MODEL: str              = 'cnn'
DEFAULT_UNKNOWN_FACE_ID: str       = 'Unknown'
TOLERANCE: float                   = 0.6
IMG_EXTs: List[str]                = ['jpg', 'jpeg', 'png']
ENCODING_EXT: str                  = 'enc'
TEXT_ENCODING: str                 = 'utf-8'

# Remove from namespace.
del sys, os, logging
