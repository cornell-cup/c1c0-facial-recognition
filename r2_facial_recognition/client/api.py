import numpy as np
import cv2


LOCAL = None
try:
    from .local import check_faces, load_images
except ImportError:
    from r2_facial_recognition.client.local import check_faces as local_check_faces, load_images as local_load_images

SCALE_FACTOR = 0.25

def set_local(filepath: str):
    global LOCAL, mappings, PATH
    LOCAL = True
    PATH = filepath
    mappings = local_load_images(filepath)


def set_remote(conn_info: dict):
    global ip, port, LOCAL
    ip = conn_info['ip']
    port = conn_info['port']
    LOCAL = False


def analyze_face(img: np.ndarray):

    resized = cv2.resize(img, (0,0), fx=SCALE_FACTOR, fy=SCALE_FACTOR)
    

    if LOCAL is None:
        raise RuntimeError('Mode unset, please call set_local or set_remote')
    elif LOCAL:
        check_faces(resized, mappings)
    else:
        pass


def load_images():
    if LOCAL is None:
        raise RuntimeError('Mode unset, please call set_local or set_remote')
    elif LOCAL:
        local_load_images()
    else:
        pass

