import os

DEFAULT_PATH = os.getenv('DEFAULT_PATH', 'resources/people')
DEFAULT_LOCAL = os.getenv('DEFAULT_LOCAL', None)
DEFAULT_CACHE = os.getenv('DEFAULT_LOCAL', True)
DEFAULT_CACHE_LOCATION = os.getenv('DEFAULT_CACHE_LOCATION', '.cache')
DEFAULT_HOST = os.getenv('DEFAULT_HOST', 'localhost')
DEFAULT_DEVICE = int(os.getenv('DEFAULT_DEVICE', 0))
# ^ change to whatever the default should be
DEFAULT_PORT = 8080  # 8080 HTTP non-privileged testing port. Use 80 for
# privilege
DEFAULT_SCALE_FACTOR = 0.25
DEFAULT_ENCODING_MODEL = 'large'
DEFAULT_NN_MODEL = 'hog'

DEFAULT_TIMEOUT = 2
DEFAULT_CHECKIN_RATE = 10  # Check-in every 10 seconds

IMG_EXTs = ['jpg', 'jpeg', 'png']
SEND_IMG = False
SEND_ENCODING = True

TEXT_ENCODING = 'utf-8'
