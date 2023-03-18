import time
import threading

# May not use

import numpy as np
import cv2

FPS = 10
SPF = 1./FPS # Seconds per frame

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Generator

class Viewer:
    def __init__(self, name):
        self.name = name
        self.event_thread = threading.Thread(self._read_img)
    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def _read_from(self, stream: Generator[np.ndarray]):
        start = time.perf_counter()
        time_since = 0
        for img in stream:
            # Max of 10 fps
            time.sleep(SPF)
            time_since = time.perf_counter() - start
            if time_since>=1.:
                start = time.perf_counter()
                time_since = 0

