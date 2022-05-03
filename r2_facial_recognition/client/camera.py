import cv2
import numpy as np
try:
    from .config import DEFAULT_DEVICE
except ImportError:
    from config import DEFAULT_DEVICE


class Camera:

    dev: cv2.VideoCapture

    def __init__(self, dev=DEFAULT_DEVICE):
        self.dev = cv2.VideoCapture(dev)
        self._dev = dev

    def __enter__(self) -> cv2.VideoCapture:
        if not self.dev.isOpened():
            self.dev.open(self._dev)
        return self.dev

    def get_frame(self):
        N = 30
        with self as cam:
            ret = False
            tries = 0
            img = None
            while not ret:
                ret, img = cam.read()
                if tries > N:
                    raise RuntimeError(f'No frames received after {N} tries.')
                tries += 1
            return img

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.dev.release()

    @staticmethod
    def find_camera(rgb_only: bool = True):
        _dev = 0
        n_devices = 10
        n_tries = 30

        while _dev < n_devices:
            cam = cv2.VideoCapture(f'/dev/video{_dev}')
            tries = 0
            ret = False
            try:
                img = None
                while not ret:
                    ret, img = cam.read()
                    if tries >= n_tries:
                        raise RuntimeError(
                            f'No frames received after {n_tries} tries.')
                    tries += 1
                if rgb_only and img is not None and not Camera.is_rgb(img):
                    raise RuntimeError('Camera is not RGB.')
                cam.release()
                return f'/dev/video{_dev}'
            except RuntimeError:
                cam.release()
                _dev += 1
                continue
        raise RuntimeError('No valid camera device found.')

    @staticmethod
    def is_rgb(img: np.ndarray, sampling: int = 5):
        width, height, depth = img.shape
        for x in range(sampling):
            for y in range(sampling):
                scaled_x = int((x/sampling)*width)
                scaled_y = int((y/sampling)*height)
                pixel = img[scaled_x, scaled_y]
                if pixel[0] != pixel[1] or pixel[1] != pixel[2] or \
                        pixel[0] != pixel[2]:
                    return True
        return False
