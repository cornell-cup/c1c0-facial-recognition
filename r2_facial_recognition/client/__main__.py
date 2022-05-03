from argparse import ArgumentParser

try:
    from .config import (
        DEFAULT_PATH, DEFAULT_LOCAL, DEFAULT_CACHE, DEFAULT_CACHE_LOCATION,
        DEFAULT_PORT, DEFAULT_HOST, DEFAULT_SCALE_FACTOR, DEFAULT_DEVICE
    )
    from .client import Client
    from .camera import Camera
except ImportError:
    from config import (
        DEFAULT_PATH, DEFAULT_LOCAL, DEFAULT_CACHE, DEFAULT_CACHE_LOCATION,
        DEFAULT_PORT, DEFAULT_HOST, DEFAULT_SCALE_FACTOR, DEFAULT_DEVICE
    )
    from client import Client
    from camera import Camera


parser = ArgumentParser()
# Add arguments
parser.add_argument('-l', '--local', action=f'store_true',
                    default=DEFAULT_LOCAL)
parser.add_argument('-nc', '--no-cache',
                    action=f'store_false', default=DEFAULT_CACHE)
# Stores
parser.add_argument('-p', '--path', action='store', default=DEFAULT_PATH)
parser.add_argument('-cl', '--cache-location', action='store',
                    default=DEFAULT_CACHE_LOCATION)
parser.add_argument('-ip', '--host', action='store', default=DEFAULT_HOST)
parser.add_argument('-P', '--port', action='store', type=int,
                    default=DEFAULT_PORT)
parser.add_argument('-in', '--input', action='store')
parser.add_argument('-d', '--device', action='store', default=DEFAULT_DEVICE)
parser.add_argument('-D', '--display', action='store_true', default=False)
# Grab the namespace
args, _ = parser.parse_known_args()

input_ = getattr(args, 'input')

# Bootstrap module with appropriate default value for LOCAL for proper
#  functionality.
# Normally, just call `api.set_[local/remote](req. params)`
# We do this here to allow full configurability.
LOCAL = getattr(args, 'local', DEFAULT_LOCAL)
CACHE = getattr(args, 'no_cache', DEFAULT_CACHE)
CACHE_LOCATION = getattr(args, 'cache_location', DEFAULT_CACHE_LOCATION)
PATH = getattr(args, 'path', DEFAULT_PATH)
HOST = getattr(args, 'host', DEFAULT_HOST)
PORT = getattr(args, 'port', DEFAULT_PORT)
DEVICE = getattr(args, 'device', DEFAULT_DEVICE)
DISPLAY = getattr(args, 'display', False)

if DEVICE == 0:
    DEVICE = Camera.find_camera()

print(DEVICE)

client = Client(local=LOCAL, path=PATH, cache=CACHE,
                cache_location=CACHE_LOCATION, ip=HOST, port=PORT, dev=DEVICE)

# Do a thing
# people, face_locations = client.interpret_task('recognize_face')
matches = client.recognize_faces(disp=DISPLAY)

