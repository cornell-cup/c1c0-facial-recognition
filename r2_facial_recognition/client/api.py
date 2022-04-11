from typing import Mapping, Optional

import numpy as np
import cv2
from requests import get, post


LOCAL = None
# LOCAL variables
MAPPINGS: Optional[Mapping[str, np.ndarray]] = None
PATH: Optional[str] = None
# REMOTE (not LOCAL) variables
IP: Optional[str] = None
PORT: Optional[int] = None

try:
    from .local import local_check_faces, local_load_images
except ImportError:
    from r2_facial_recognition.client.local import (
        local_check_faces, local_load_images
    )


SCALE_FACTOR = 0.25


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
        local_check_faces(resized, MAPPINGS)
    else:
        # Wish I could send image directly over get since it is not changing
        # data on the server, but unfortunately not possible. Would have to
        # convert to Base64... maybe try it later and test speed later.
        # get(f'{IP}:{PORT}', params=())
        post(f'{IP}:{PORT}/analyze_face', files=img.tobytes())


def load_images():
    if LOCAL is None:
        raise RuntimeError('Mode unset, please call set_local or set_remote')
    elif LOCAL:
        local_load_images(PATH, MAPPINGS)
    else:
        get(f'{IP}:{PORT}/load_images')

