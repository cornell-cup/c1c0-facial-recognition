import time
import threading
import json
import sys

from requests import get, post, HTTPError, ConnectionError
import numpy as np
import cv2

from r2_facial_recognition.client.config import DEFAULT_LOCAL, DEFAULT_CACHE, DEFAULT_CACHE_LOCATION, \
    DEFAULT_PATH, DEFAULT_SCALE_FACTOR, DEFAULT_HOST, DEFAULT_PORT, \
    DEFAULT_DEVICE, DEFAULT_TIMEOUT, DEFAULT_CHECKIN_RATE, TEXT_ENCODING, DEFAULT_UNKNOWN_FACE_ID
from r2_facial_recognition.client.camera import Camera
from r2_facial_recognition.client.local_recognition import check_faces as local_check_faces, load_images as local_load_images


import logging

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Optional, List, Mapping, Tuple, Callable, Sized, Iterable, Any

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

UNKNOWN_FACE = DEFAULT_UNKNOWN_FACE_ID

class InvalidParameter(ValueError):
    pass

class Client:
    # camera: Camera

    def learn_face(self, name: str ,disp: bool = False, best_of_n: int = 3, *_, **__):
        with self.camera:
            img = self.camera.read()
            detected_face = local_check_faces(img, self.encoding_map)
            if detected_face != UNKNOWN_FACE:
                # Handle case where c1c0 thinks user already exists.
                pass



    def take_attendance(self, disp: bool = False, *_, **__):
        """
        Takes a series of pictures as C1C0 turns, makes a request to the
        backend for each picture and unions the results of facial recognition.

        Outputs the matches and asks for confirmation from chatbot.
        """
        n_imgs = 3
        res = set()
        # take all 3 pictures then call recognize faces
        def analyze(image):
            results = self.analyze_faces(image)
            res.update(name for name, _ in results['matches'] if name != UNKNOWN_FACE)
            print('analyzing')
            if disp:
                # print('displaying')
                for name, (top, right, bottom, left) in results['matches']:
                    cv2.putText(image, name, (left - 20, bottom + 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.imshow('Detected faces', image)
                if cv2.waitKey(25) & 0xFF == ord('q'):
                    sys.exit(0)
        workers = []
        with self.camera as cam:
            # TODO: Write fold-join
            # Did not need to name it cam, self.camera == cam. But wanted to anyway
            workers.append(threading.Thread(target=analyze, args=(cam.read(),), daemon=True))
            workers[0].start()
            # turn left 10 degrees
            print('C1C0 TURN LEFT')
            time.sleep(3)
            workers.append(threading.Thread(target=analyze, args=(cam.read(),), daemon=True))
            workers[1].start()
            # turn right 20 degrees
            print('C1C0 TURN RIGHT')
            time.sleep(3)
            workers.append(threading.Thread(target=analyze, args=(cam.read(),), daemon=True))
            workers[2].start()

        return res

    def __init__(self,  local: 'Optional[bool]' = DEFAULT_LOCAL,
                 path: str = DEFAULT_PATH, cache: bool = DEFAULT_CACHE,
                 cache_location: str = DEFAULT_CACHE_LOCATION,
                 mappings=None, ip=DEFAULT_HOST, port=DEFAULT_PORT,
                 dev: str = DEFAULT_DEVICE, scale_factor: float =
                 DEFAULT_SCALE_FACTOR, timeout: float = DEFAULT_TIMEOUT,
                 check_in_rate: float = DEFAULT_CHECKIN_RATE):
        # api.load_images()
        self.camera = Camera(dev)
        self._task_map = {
            'learn_face': self.learn_face,
            'take_attendance': self.take_attendance
        }
        self._local = local
        self._path = path
        self.use_cache = cache
        self.cache_location = cache_location
        self.encoding_map = mappings if mappings is not None else {}
        self._ip = ip
        self._port = port
        self.scale_factor = DEFAULT_SCALE_FACTOR if scale_factor is None else \
            scale_factor
        self.timeout = timeout
        self._last_result = (False, 0)
        self._check_in_rate = check_in_rate
        self.load_images()

    def get_conn_str(self):
        return f'http://{self._ip}:{self._port}'

    def is_local(self):
        if self._local is not None:
            return self._local
        last_result, last_time = self._last_result
        if time.time() - last_time < self._check_in_rate:
            return last_result
        # Need to update check-in algo
        result = True
        try:
            resp = get(self.get_conn_str(), timeout=self.timeout)
            resp.raise_for_status()
        except (ConnectionError, HTTPError):
            result = False
        self._last_result = (result, time.time())
        return result

    def interpret_task(self, task):

        return self._task_map[task]

    def set_local(self, filepath: str, force: bool = True):
        self._path = self._path if filepath is None else filepath
        self.encoding_map = self.encoding_map if filepath is None else \
            local_load_images(filepath)
        if force:
            self._local = True

    def set_remote(self, ip: 'Optional[str]' = None, port: 'Optional[int]' = None,
                   force: bool = True):
        self._ip = self._ip if ip is None else ip
        self._port = self._port if port is None else port
        if force:
            self._local = False

    def set_auto(self):
        self._local = None

    def analyze_faces(self, img: np.ndarray) -> \
            'Mapping[str, List[Tuple[str, Tuple[int, int, int, int]]]]':
        resized = cv2.resize(img, (0, 0), fx=self.scale_factor,
                             fy=self.scale_factor)

        if self.is_local():
            return {
                'matches': local_check_faces(resized, self.encoding_map),
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
            result = local_load_images(self._path, self.encoding_map,
                                       cache=self.use_cache,
                                       cache_location=self.cache_location)
            logger.info('Images loaded.')
            return result
        else:
            # Not necessary due to server startup magic. see
            #  r2_facial_recognition_server
            return True

    def get_actions(self) -> 'List[str]':
        return list(self._task_map.keys())
