from typing import Optional, List, Mapping, Tuple
import numpy as np
from scipy.ndimage import gaussian_filter
import cv2
import time
import tkinter as tk
from PIL import Image, ImageTk
from gamlogger import get_default_logger
from requests import get, post, HTTPError, ConnectionError
import json
from os import path

from .config import DEFAULT_LOCAL, DEFAULT_CACHE, DEFAULT_CACHE_LOCATION, \
    DEFAULT_PATH, DEFAULT_SCALE_FACTOR, DEFAULT_HOST, DEFAULT_PORT, \
    DEFAULT_DEVICE, DEFAULT_TIMEOUT, DEFAULT_CHECKIN_RATE, TEXT_ENCODING
from .camera import Camera
from .local import local_load_images, local_check_faces
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
            if name == 'Unknown':
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

    # https://stackoverflow.com/questions/32609098/how-to-fast-change-image-brightness-with-python-opencv
    def increase_brightness(self, img, order = 0.5):
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        v = (255 ** order * v.astype(np.float64) ** (1 - order)).astype(np.uint8)
        final_hsv = cv2.merge((h, s, v))
        img = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
        return img

    # https://stackoverflow.com/questions/46390779/automatic-white-balancing-with-grayworld-assumption
    def white_balance(self, img):
        result = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        avg_a = np.average(result[:, :, 1])
        avg_b = np.average(result[:, :, 2])
        result[:, :, 1] = result[:, :, 1] - ((avg_a - 128) * (result[:, :, 0] / 255.0) * 1.1)
        result[:, :, 2] = result[:, :, 2] - ((avg_b - 128) * (result[:, :, 0] / 255.0) * 1.1)
        result = cv2.cvtColor(result, cv2.COLOR_LAB2BGR)
        return result
    
    def sharpen(self, img, w = 0.5):
        colors = [i.astype(np.float64) for i in cv2.split(img)]
        smooth_colors = []
        for c in colors:
            smooth_colors.append(gaussian_filter(c, 1.5))
        ans = [np.clip(((1 + w) * c - w * s), 0, 255).astype(np.uint8) for s, c in zip(smooth_colors, colors)]
        return cv2.merge(tuple(ans))


    def take_attendance(self, local = False, *_, **__):
        """
        Takes a series of pictures as C1C0 turns, makes a request to the 
        backend for each picture and unions the results of facial recognition.

        Outputs the matches and asks for confirmation from chatbot.
        """
        res = set()
        # take all 3 pictures then call recognize faces
        images = []
        if local:
            images = [cv2.imread(path.join(path.dirname(__file__), '../../data/image '+ str(i) + '.png') ) for i in range(8)]
        else:
            img1 = self.camera.get_frame()
            # cv2.imshow("img1", img1)
            # cv2.waitKey(1000)
            images.append(img1)
            # turn left 10 degrees
            print('TURN LEFT')
            time.sleep(3)
            img2 = self.camera.get_frame()
            # cv2.imshow("img2", img2)
            # cv2.waitKey(1000)
            images.append(img2)
            # turn right 20 degrees
            print('TURN RIGHT')
            time.sleep(3)
            img3 = self.camera.get_frame()
            # cv2.imshow("img3", img3)
            # cv2.waitKey(1000)
            images.append(img3)
        
        images = [self.sharpen(self.white_balance(self.increase_brightness(img)), w = 1) for img in images]
        bounding_boxes = [[] for _ in images]
        for i, image in enumerate(images):
            matches = self.analyze_faces(image)['matches']
            for name, bounding_box in matches:
                if name != 'Unknown':
                    res.add(name)
                    bounding_boxes[i].append((bounding_box, name.replace('_', ' ')))
        for i in range(len(images)):
            for box, name in bounding_boxes[i]:
                top, right, bottom, left = box
                width = right - left
                height = bottom - top
                top -= height//5
                bottom += height//5
                left -= width//5
                right += width//5
                
                images[i] = cv2.rectangle(images[i], (left, top), (right, bottom), (255, 0, 0), 2)
                images[i] = cv2.putText(images[i], name, (left, bottom+15),cv2.FONT_HERSHEY_SIMPLEX, .5, (255, 0, 0), 2, cv2.LINE_AA)
                images[i] = cv2.putText(images[i], name, (left, bottom+15),cv2.FONT_HERSHEY_SIMPLEX, .5, (255, 255, 255), 1, cv2.LINE_AA)

        
        print(bounding_boxes)
        concat_img = np.concatenate(tuple(images), axis=1)
        cv2.imshow("Result", concat_img)
        cv2.waitKey()

        return res

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
