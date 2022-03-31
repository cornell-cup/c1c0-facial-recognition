from argparse import ArgumentParser

DEFAULT_PATH = '.cache'
DEFAULT_LOCAL = False
DEFAULT_CACHE = True


parser = ArgumentParser()
parser.add_argument('-l', '--local',
                    action=f'store_{str(not DEFAULT_LOCAL).lower()}')
parser.add_argument('-nc', '--no-cache',
                    action=f'store_{str(not DEFAULT_CACHE).lower()}')
parser.add_argument('-p', '--path', action='store', default='.cache')

args, _ = parser.parse_known_args()
local = getattr(args, 'local', DEFAULT_LOCAL)
cache = getattr(args, 'no_cache', DEFAULT_CACHE)
path = getattr(args, 'path', DEFAULT_PATH)


if local:
    try:
        from . import local as api
    except ImportError:
        from r2_facial_recognition.client import local as api
# else:
    # Do server api import
    # temp:
    try:
        from . import local as api
    except ImportError:
        from r2_facial_recognition.client import local as api

mappings = api.load_images(path, cache_location=cache)

