import cv2
import numpy as np

from r2_facial_recognition.client.config import DEFAULT_DEVICE

# Linter setup
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional


class DeviceError(OSError):
    pass
class Camera:
    """
    A wrapper around cv2.VideoCapture, see
    https://docs.opencv.org/3.4/d8/dfe/classcv_1_1VideoCapture.html
    """
    dev: cv2.VideoCapture

    def __init__(self, dev:'Optional[int]' = DEFAULT_DEVICE, n_tries = 30):
        """
        Facial Recognition camera.

        PARAMETERS
        ----------
        dev -
            Device ID for the camera. Refer to cv2.VideoCapture. If None, will
            call Camera.find_camera() to get the camera. By default will use the config value, DEFAULT_DEVICE.
        """
        self._dev = Camera.find_camera() if dev is None else dev
        self.dev = cv2.VideoCapture(self._dev)
        self.n_tries = n_tries

    def __enter__(self) -> 'Camera':
        if not self.dev.isOpened():
            if not self.dev.open(self._dev):
                raise DeviceError(f'Unable to open device at index: {self._dev}')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.dev.release()

    def read(self, n_tries = None):
        n_tries = self.n_tries if n_tries is None else n_tries
        for _ in range(n_tries):
            ret, img = self.dev.read()
            if ret:
                return img
        raise DeviceError(f'No frames received after {n_tries} tries.')

    @staticmethod
    def find_camera(rgb_only: bool = True, n_devices = 10, n_tries = 30):
        _dev = 0

        while _dev < n_devices:
            cam = cv2.VideoCapture(_dev)
            if not cam.isOpened():
                _dev += 1
                continue
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
                return _dev
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
