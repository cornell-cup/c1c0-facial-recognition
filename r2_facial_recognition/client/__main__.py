from argparse import ArgumentParser
import cv2

try:
    from . import api
    from .config import (
        DEFAULT_PATH, DEFAULT_LOCAL, DEFAULT_CACHE, DEFAULT_CACHE_LOCATION,
        DEFAULT_PORT, DEFAULT_IP, DEFAULT_SCALE_FACTOR
    )
except ImportError:
    from r2_facial_recognition.client import api
    from r2_facial_recognition.client.config import (
        DEFAULT_PATH, DEFAULT_LOCAL, DEFAULT_CACHE, DEFAULT_CACHE_LOCATION,
        DEFAULT_PORT, DEFAULT_IP, DEFAULT_SCALE_FACTOR
    )


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
parser.add_argument('-ip', '--host', action='store', default=DEFAULT_IP)
parser.add_argument('-P', '--port', action='store', type=int,
                    default=DEFAULT_PORT)
parser.add_argument('-in', '--input', action='store', required=True)
# Grab the namespace
args, _ = parser.parse_known_args()

input_ = getattr(args, 'input')

# Bootstrap module with appropriate default value for LOCAL for proper
#  functionality.
# Normally, just call `api.set_[local/remote](req. params)`
# We do this here to allow full configurability.
api.LOCAL = getattr(args, 'local', DEFAULT_LOCAL)
print(api.LOCAL)
print(args)
api.CACHE = getattr(args, 'no_cache', DEFAULT_CACHE)
api.CACHE_LOCATION = getattr(args, 'cache_location', DEFAULT_CACHE_LOCATION)
api.PATH = getattr(args, 'path', DEFAULT_PATH)
api.MAPPINGS = api.load_images()

# Do a thing
img = cv2.imread(input_)
people, face_locations = api.analyze_face(img)
img = cv2.resize(img, (0, 0), fx=DEFAULT_SCALE_FACTOR, fy=DEFAULT_SCALE_FACTOR)

data = dict(zip(people, face_locations))
# from face_recognition import face_locations
# face_locations_ = face_locations(img)

# for top, right, bottom, left in unknown_face_locs:
#     cv2.rectangle(img, (top, right), (bottom, left), (0, 255, 0), 1)
# print(face_locations_)
print(data)
for person, (top, right, bottom, left) in data.items():
    cv2.rectangle(img, (right, top), (left, bottom), (0, 255, 0), 2)
    cv2.putText(img, person, (left, bottom+25), cv2.FONT_HERSHEY_SIMPLEX, 0.9,
                (0, 255, 0), 2)

cv2.imshow('Unknown Faces', img)
cv2.waitKey(0)
