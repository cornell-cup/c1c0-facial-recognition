import cv2
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
