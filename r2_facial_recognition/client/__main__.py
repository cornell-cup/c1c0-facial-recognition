"""
This module is fully controllable using command line arguments. See the help
for each of the below added arguments for usage instructions.
"""
from argparse import ArgumentParser

from .config import (
    DEFAULT_PATH, DEFAULT_LOCAL, DEFAULT_CACHE, DEFAULT_CACHE_LOCATION,
    DEFAULT_PORT, DEFAULT_HOST, DEFAULT_SCALE_FACTOR, DEFAULT_DEVICE
)
from .client import Client
from .camera import Camera


parser = ArgumentParser()
# Add arguments
# Flags
parser.add_argument('-l', '--local', action='store_true',
                    default=DEFAULT_LOCAL,
                    help='Tells the Facial Recognition Client to run in '
                         'local-only mode. [-r/--remote] wins out if both are'
                         'present.')
parser.add_argument('-r', '--remote', action='store_true',
                    help='Tells the Facial Recognition Client to run in'
                         'remote-only mode. [-l/--local] loses out if both are'
                         'present.')
parser.add_argument('-nc', '--no-cache',
                    action=f'store_false', default=DEFAULT_CACHE,
                    help='Whether or not to save the file encodings on the'
                         'local filesystem once they are generated, or whether'
                         'to store them only in memory. This only applies when'
                         'running locally.')
# Stores
parser.add_argument('-p', '--path', action='store', default=DEFAULT_PATH,
                    help='The path where the training headshots are stored.'
                         'This is only applicable when running locally.')
parser.add_argument('-cl', '--cache-location', action='store',
                    default=DEFAULT_CACHE_LOCATION,
                    help='The location to cache processed/trained headshots, '
                         'optionally disabled with [-nc/--no-cache].')
parser.add_argument('-ip', '--host', action='store', default=DEFAULT_HOST,
                    help='The host ip-address. The protocol is not necessary '
                         'to pass, just a valid IP address that is running an '
                         'instance of the r2_facial_recognition server.')
parser.add_argument('-P', '--port', action='store', type=int,
                    default=DEFAULT_PORT,
                    help='The port for the server. The default is 8080, though'
                         'Flask development servers tend to run on port 5000.')
parser.add_argument('-in', '--input', action='store',
                    help='The location of the input file to run the '
                         'module-level facial recognition code. This will'
                         'analyze the headshot and print out the recognized'
                         'face and location. This is required if [-d/--device]'
                         ' is not defined.')
parser.add_argument('-d', '--device', action='store', default=DEFAULT_DEVICE,
                    help='The device to use for taking a picture to analyze'
                         'against. This is required if [-in/--input] is not '
                         'defined.')
parser.add_argument('-D', '--display', action='store_true', default=False,
                    help='Whether to display the results when they are '
                         'generated or not.')
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
DISPLAY = getattr(args, 'display', False)
REMOTE = getattr(args, 'remote', False)
LOCAL = False if REMOTE else LOCAL
DEVICE = getattr(args, 'device', DEFAULT_DEVICE)
try:
     DEVICE = DEVICE if DEVICE > 0 else Camera.find_camera()
except Exception:
     pass


client = Client(local=LOCAL, path=PATH, cache=CACHE,
                cache_location=CACHE_LOCATION, ip=HOST, port=PORT, dev=DEVICE)

# Do a thing
# people, face_locations = client.interpret_task('recognize_face')
# matches = client.recognize_faces(disp=DISPLAY)
# print(matches)
matches = client.take_attendance(local=False)
print(matches)

