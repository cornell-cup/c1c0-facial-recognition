import sys, os, logging

from typing import List

# Computer architecture config.
DEFAULT_PATH: str            = os.getenv('DEFAULT_PATH', 'resources/people')
DEFAULT_LOCAL: bool          = os.getenv('DEFAULT_LOCAL', True)
DEFAULT_CACHE: bool          = os.getenv('DEFAULT_CACHE', True)
DEFAULT_CACHE_LOCATION: str  = os.getenv('DEFAULT_CACHE_LOCATION', '.cache')
DEFAULT_HOST: str            = os.getenv('DEFAULT_HOST', '127.0.0.1')
DEFAULT_DEVICE: int          = int(os.getenv('DEFAULT_DEVICE', -1))
DEFAULT_PORT: int            = 1233  # 8080 non-privilege or 80 privilege.

# Facial recognition config.
DEFAULT_SCALE_FACTOR: float  = 0.25
DEFAULT_ENCODING_MODEL: str  = 'large'
DEFAULT_NN_MODEL: str        = 'hog'
DEFAULT_UNKNOWN_FACE_ID: str = 'Unknown'
DEFAULT_TIMEOUT: int         = 10
DEFAULT_CHECKIN_RATE: int    = 10
IMG_EXTs: List[str]          = ['jpg', 'jpeg', 'png']
SEND_IMG: bool               = False
SEND_ENCODING: bool          = True
TEXT_ENCODING: str           = 'utf-8'

# Logging config.
LOG_FILE: str                = os.path.join(os.getcwd(), 'facial_recognition.log')
LOG_LEVEL: int               = logging.INFO # INFO, WARNING, ERROR, CRITICAL, FATAL.

# Remove from namespace.
del sys, os, logging
