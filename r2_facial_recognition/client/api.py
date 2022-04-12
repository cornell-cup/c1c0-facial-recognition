from typing import Mapping, Optional

import numpy as np
import cv2
from requests import get, post

try:
    from .config import (
        DEFAULT_PATH, DEFAULT_LOCAL, DEFAULT_CACHE, DEFAULT_CACHE_LOCATION,
        DEFAULT_PORT, DEFAULT_IP, DEFAULT_SCALE_FACTOR
    )
except ImportError:
    from r2_facial_recognition.client.config import (
        DEFAULT_PATH, DEFAULT_LOCAL, DEFAULT_CACHE, DEFAULT_CACHE_LOCATION,
        DEFAULT_PORT, DEFAULT_IP, DEFAULT_SCALE_FACTOR
    )

LOCAL = DEFAULT_LOCAL
CACHE = DEFAULT_CACHE
CACHE_LOCATION = DEFAULT_CACHE_LOCATION
IMAGES_LOADED = False
# LOCAL variables
MAPPINGS: Optional[Mapping[str, np.ndarray]] = None
PATH: Optional[str] = DEFAULT_PATH
# REMOTE (not LOCAL) variables
IP: Optional[str] = DEFAULT_IP
PORT: Optional[int] = DEFAULT_PORT
SCALE_FACTOR: float = DEFAULT_SCALE_FACTOR

try:
    from .local import local_check_faces, local_load_images
except ImportError:
    from r2_facial_recognition.client.local import (
        local_check_faces, local_load_images
    )


def set_local(filepath: str):
    global LOCAL, MAPPINGS, PATH
    LOCAL = True
    PATH = filepath if filepath is not None else PATH
    MAPPINGS = local_load_images(filepath) if filepath is not None else \
        MAPPINGS


def set_remote(ip: Optional[str] = None, port: Optional[int] = None):
    global LOCAL, IP, PORT
    LOCAL = False
    IP = ip if ip is not None else IP
    PORT = port if port is not None else PORT


def analyze_face(img: np.ndarray):

    resized = cv2.resize(img, (0, 0), fx=SCALE_FACTOR, fy=SCALE_FACTOR)

    if LOCAL is None:
        raise RuntimeError('Mode unset, please call set_local or set_remote')
    elif LOCAL:
        identities, unknown_faces = local_check_faces(resized, MAPPINGS)
        return identities, unknown_faces
    else:
        # Wish I could send image directly over get since it is not changing
        # data on the server, but unfortunately not possible. Would have to
        # convert to Base64... maybe try it later and test speed later.
        # get(f'{IP}:{PORT}', params=())
        return post(f'{IP}:{PORT}/analyze_face', files=img.tobytes(),
                    data={'cache': CACHE, 'cache_location': CACHE_LOCATION})


def load_images():
    global IMAGES_LOADED
    failed = False
    try:
        if LOCAL is None:
            failed = True
            raise RuntimeError('Mode unset, please call set_local or '
                               'set_remote')
        elif LOCAL:
            return local_load_images(PATH, MAPPINGS, cache=CACHE,
                                     cache_location=CACHE_LOCATION)
        else:
            return get(f'{IP}:{PORT}/load_images',
                       params={'cache': CACHE, 'cache_location': CACHE_LOCATION
                               })
    finally:
        IMAGES_LOADED = IMAGES_LOADED if failed else True
