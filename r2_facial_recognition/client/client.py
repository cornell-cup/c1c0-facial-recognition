from typing import Optional, List, Mapping, Tuple
import numpy as np
import cv2
from time import time

from gamlogger import get_default_logger
from requests import get, post, HTTPError
import json

try:
    from .config import DEFAULT_LOCAL, DEFAULT_CACHE, DEFAULT_CACHE_LOCATION, \
        DEFAULT_PATH, DEFAULT_SCALE_FACTOR, DEFAULT_HOST, DEFAULT_PORT, \
        DEFAULT_DEVICE, DEFAULT_TIMEOUT, DEFAULT_CHECKIN_RATE, TEXT_ENCODING
    from .camera import Camera
    from .local import local_load_images, local_check_faces
except ImportError:
    from config import DEFAULT_LOCAL, DEFAULT_CACHE, DEFAULT_CACHE_LOCATION, \
        DEFAULT_PATH, DEFAULT_SCALE_FACTOR, DEFAULT_HOST, DEFAULT_PORT, \
        DEFAULT_DEVICE, DEFAULT_TIMEOUT, DEFAULT_CHECKIN_RATE, TEXT_ENCODING
    from camera import Camera
    from local import local_load_images, local_check_faces

logger = get_default_logger(__name__)


class Client:
    def recognize_faces(self, disp: bool = False, best_of_n: int = 3,
                        *_, **__):
        matching_attempts = []
        img = None
        for i in range(best_of_n):
            img = self.camera.get_frame()
            result = self.analyze_faces(img)
            matching_attempts.extend(result['matches'])
        matches = {}
        unknowns = 0
        for name, loc in matching_attempts:
            if name == 'Unknown_Person':
                name = f'{name}{unknowns}'
                unknowns += 1
            matches[name] = loc

        if disp:
            for name, (top, right, bottom, left) in matches.items():
                cv2.putText(img, name, (left - 20, bottom + 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow('Detected faces', img)
            cv2.waitKey(0)
        return matches

    def take_attendance(self, group, *_, **__):
        pass

    def __init__(self,  local: Optional[bool] = DEFAULT_LOCAL,
                 path: str = DEFAULT_PATH, cache: bool = DEFAULT_CACHE,
                 cache_location: str = DEFAULT_CACHE_LOCATION,
                 mappings=None, ip=DEFAULT_HOST, port=DEFAULT_PORT,
                 dev: str = DEFAULT_DEVICE, scale_factor: float =
                 DEFAULT_SCALE_FACTOR, timeout: float = DEFAULT_TIMEOUT,
                 check_in_rate: float = DEFAULT_CHECKIN_RATE):
        # api.load_images()
        self.camera = Camera(dev)
        self._task_map = {
            'recognize_face': self.recognize_faces,
            'take_attendance': self.take_attendance
        }
        self._local = local
        self._path = path
        self.use_cache = cache
        self.cache_location = cache_location
        self._mappings = mappings if mappings is not None else {}
        self._ip = ip
        self._port = port
        self.scale_factor = DEFAULT_SCALE_FACTOR if scale_factor is None else \
            scale_factor
        self.timeout = timeout
        self._last_result = (False, 0)
        self._check_in_rate = check_in_rate
        self.load_images()

    def get_conn_str(self):
        return f'http://{self._ip}:{self._port}/'

    def is_local(self):
        if self._local is not None:
            return self._local
        last_result, last_time = self._last_result
        if time() - last_time < self._check_in_rate:
            return last_result
        print(self.get_conn_str())
        # Need to update check-in algo
        resp = get(self.get_conn_str(), timeout=self.timeout)
        result = True
        try:
            resp.raise_for_status()
        except HTTPError:
            result = False
        self._last_result = (result, time())
        return result

    def interpret_task(self, task):
        return self._task_map[task]

    def set_local(self, filepath: str, force: bool = True):
        self._path = self._path if filepath is None else filepath
        self._mappings = self._mappings if filepath is None else \
            local_load_images(filepath)
        if force:
            self._local = True

    def set_remote(self, ip: Optional[str] = None, port: Optional[int] = None,
                   force: bool = True):
        self._ip = self._ip if ip is None else ip
        self._port = self._port if port is None else port
        if force:
            self._local = False

    def set_auto(self):
        self._local = None

    def analyze_faces(self, img: np.ndarray) -> \
            Mapping[str, List[Tuple[str, Tuple[int, int, int, int]]]]:
        resized = cv2.resize(img, (0, 0), fx=self.scale_factor,
                             fy=self.scale_factor)

        if self.is_local():
            return {
                'matches': local_check_faces(resized, self._mappings),
                'face_locations': []
            }
        else:
            # Wish I could send image directly over get since it is not
            # changing data on the server, but unfortunately not possible.
            # Would have to convert to Base64... maybe try and test speed
            # later.
            # get(f'{IP}:{PORT}', params=())
            resp = post(f'{self.get_conn_str()}/face_recognition/detect',
                        files={'image': img.tobytes()},
                        data={
                            'cache': self.use_cache,
                            'cache_location': self.cache_location,
                            'shape': str(img.shape)
                        })
            resp.raise_for_status()
            return json.loads(resp.content.decode(TEXT_ENCODING))

    def load_images(self):
        logger.info('Loading images')
        if self.is_local():
            result = local_load_images(self._path, self._mappings,
                                       cache=self.use_cache,
                                       cache_location=self.cache_location)
            logger.info('Images loaded.')
            return result
        else:
            # Not necessary due to server startup magic. see
            #  r2_facial_recognition_server
            return True

    def get_actions(self) -> List[str]:
        return list(self._task_map.keys())
