from argparse import ArgumentParser
import cv2

try:
    from . import api
except ImportError:
    from r2_facial_recognition.client import api

DEFAULT_PATH = 'resources/people'
DEFAULT_LOCAL = False
DEFAULT_CACHE = True
DEFAULT_CACHE_LOCATION = '.cache'
DEFAULT_IP = '192.168.1.5'  # change to whatever the default should be
DEFAULT_PORT = 8080  # 8080 HTTP non-privileged testing port. Use 80 for
# privilege


parser = ArgumentParser()
# Add arguments
parser.add_argument('-l', '--local',
                    action=f'store_{str(not DEFAULT_LOCAL).lower()}')
parser.add_argument('-nc', '--no-cache',
                    action=f'store_{str(not DEFAULT_CACHE).lower()}')
# Stores
parser.add_argument('-p', '--path', action='store', default=DEFAULT_PATH)
parser.add_argument('-cl', '--cache-location', action='store',
                    default=DEFAULT_CACHE_LOCATION)
parser.add_argument('-ip', '--host', action='store', default=DEFAULT_IP)
parser.add_argument('-P', '--port', action='store', type=int,
                    default=DEFAULT_PORT)
# Grab the namespace
args, _ = parser.parse_known_args()

cache_location = getattr(args, 'cache_loc', DEFAULT_CACHE_LOCATION)

# Bootstrap module with appropriate default value for LOCAL for proper
#  functionality.
api.LOCAL = getattr(args, 'local', DEFAULT_LOCAL)
api.CACHE = getattr(args, 'no_cache', DEFAULT_CACHE)
api.CACHE_LOCATION = getattr(args, 'cache_location', DEFAULT_CACHE_LOCATION)
api.PATH = getattr(args, 'path', DEFAULT_PATH)

api.MAPPINGS = api.load_images()
# Load image
img = cv2.imread('kassy.jpg')
img = cv2.resize(img, (0, 0), fx=.25, fy=.25)
print(api.analyze_face(img))
