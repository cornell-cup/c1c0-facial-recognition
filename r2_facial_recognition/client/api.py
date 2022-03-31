import numpy as np


LOCAL = None
from .local import check_faces, load_images


def set_local(filepath: str):
    global LOCAL
    LOCAL = False
    load_images()


def set_remote(conn_info: dict):
    global ip, port, LOCAL
    ip = conn_info['ip']
    port = conn_info['port']
    LOCAL = False


def analyze_face(img: np.ndarray):
    if LOCAL is None:
        raise RuntimeError('Mode unset, please call set_local or set_remote')
    elif LOCAL:
        pass
    else:
        pass


def load_images():
    if LOCAL is None:
        raise RuntimeError('Mode unset, please call set_local or set_remote')
    elif LOCAL:
        pass        
    else:
        pass


def check_faces():
    if LOCAL is None:
        raise RuntimeError('Mode unset, please call set_local or set_remote')
    elif LOCAL:
        pass        
    else:
        pass
