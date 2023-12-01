from requests import get, post, HTTPError, ConnectionError
import time, threading, json, cv2, logging
import matplotlib.pyplot as plt
import numpy as np

from client.classify import check_faces, local_load_images, local_load_cache, check_and_add_file, check_and_add_img
from client.camera import Camera
import client.rotation as rotate
from client.config import *

from typing import Optional, List, Mapping, Tuple, Set

# Config values
UNKNOWN_FACE: str = DEFAULT_UNKNOWN_FACE_ID
class InvalidParameter(ValueError): pass

class Client:
	"""
	Class representing the main bulk of the facial recognition client. Used to classify
	images and send results to scheduler.
	"""

	camera: Camera
	disp_lock: threading.Lock = threading.Lock()
	face_number: int = 0
	stall: float = 1.0

	def display(self: any, img: np.ndarray, results: List[Tuple[str, Tuple[int, int, int, int]]]) -> None:
		for i, (name, (top, right, bottom, left)) in enumerate(results):
			top = int(top / self.scale_factor);       right = int(right / self.scale_factor)
			bottom = int(bottom / self.scale_factor); left = int(left / self.scale_factor)
			color: Tuple[int, int, int] = COLORS[i % len(COLORS)];

			cv2.rectangle(img, (left, top), (right, bottom), color, 2)
			cv2.putText(img, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, color, 2)

		WINDOW_NAME: str = 'Recognized Faces: Frame ' + str(Client.face_number);
		cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_AUTOSIZE); Client.face_number += 1
		cv2.imshow(WINDOW_NAME, img); cv2.waitKey(0)
		cv2.waitKey(1); cv2.destroyWindow(WINDOW_NAME); cv2.waitKey(1)

	def learn_face(self: any, names: List[str], disp: bool = False, *_, **__) -> List[str]:
		"""
		Given a name, will take a picture and create a mapping from that name to the
		approriate facial encodings.

		PARAMETERS
		----------
		name - Name of the face in the image.
		disp - Whether or not to display the image with bounding boxes.
		"""
		name = ' '.join(names) if len(names) > 0 else "Face Number " + str(Client.face_number)

		with self.camera as cam:
			print('Taking picture and starting analyzation process.')
			time.sleep(self.stall); img: np.ndarray = cam.adjust_read()

			print(f'Analyzing image: {img[0][0]}, {img[0][1]}, {img[0][2]}, ...')
			check_and_add_img(img, name, self.encoding_map, cache=self.use_cache, cache_location=self.cache_location)
			results: any = self.analyze_faces(img)['matches']
			pruned: any = [(name, loc) for name, loc in results if name != UNKNOWN_FACE]

			if (disp): self.display(img, results)

		names: Set[str] = {name for name, _ in pruned}
		formatted: str = "[" + ", ".join(names) + "]"
		print(f"Recognized: {formatted}"); return names


	def take_attendance(self: any, disp: bool = False, *_, **__) -> List[str]:
		"""
		Takes a picture and returns a list of names of people recognized in the image.
		Also displays the image with bounding boxes if disp is true.

		PARAMETERS
		----------
		disp - Whether or not to display the image with bounding boxes.
		"""

		with self.camera as cam:
			print('Taking picture and starting analyzation process.')
			time.sleep(self.stall); img: np.ndarray = cam.adjust_read()

			print(f'Analyzing image: {img[0][0]}, {img[0][1]}, {img[0][2]}, ...')
			results: any = self.analyze_faces(img)['matches']
			pruned: any = [(name, loc) for name, loc in results if name != UNKNOWN_FACE]

			if (disp): self.display(img, results)

		names: Set[str] = {name for name, _ in pruned}
		formatted: str = "[" + ", ".join(names) + "]"
		print(f"Recognized: {formatted}"); return names

	def __init__(self: any, local: Optional[bool] = DEFAULT_LOCAL, path: str = DEFAULT_PATH, open: bool = DEFAULT_OPEN,
				 load: bool = DEFAULT_LOAD, cache: bool = DEFAULT_CACHE, cache_location: str = DEFAULT_CACHE_LOCATION,
                 mappings = None, ip = DEFAULT_HOST, port = DEFAULT_PORT, dev: str = DEFAULT_DEVICE,
				 scale_factor: float = DEFAULT_SCALE_FACTOR, timeout: float = DEFAULT_TIMEOUT,
                 check_in_rate: float = DEFAULT_CHECKIN_RATE) -> 'Client':
		"""
		Initializes an instance of client with a lot of default values and configurations.
		"""

		self.camera = Camera(dev) if open else None
		self.task_map = {
			'learn': (lambda names: self.learn_face(names, disp=True)),
			'l': (lambda names: self.learn_face(names, disp=True)),
			'attendance': (lambda _: self.take_attendance(disp=True)),
			'a': (lambda _: self.take_attendance(disp=True)),
		}
		self.local = local
		self.path = path
		self.load_img = load
		self.use_cache = cache
		self.cache_location = cache_location
		self.encoding_map = mappings if mappings is not None else {}
		self.ip = ip
		self.port = port
		self.scale_factor = DEFAULT_SCALE_FACTOR if scale_factor is None else scale_factor
		self.timeout = timeout
		self.last_result = (False, 0)
		self.check_in_rate = check_in_rate
		if (load): self.load_images()
		if (cache): self.load_cache()

	def get_conn_str(self: any) -> str:
		"""
		Returns URL connection string used for post and get requests.
		"""

		return f'http://{self._ip}:{self._port}'

	def is_local(self: any) -> bool:
		"""
		Returns the result of an image to determine if the client is currently local or not.
		"""

		if self.local is not None: return self.local
		last_result: bool; last_time: int
		last_result, last_time = self.last_result

		if time.time() - last_time < self._check_in_rate: return last_result
		result: bool = True

		try:
			resp = get(self.get_conn_str(), timeout=self.timeout)
			resp.raise_for_status()

		except (ConnectionError, HTTPError): result = False

		self.last_result = (result, time.time())
		return result

	def interpret_task(self: any, task: str) -> any:
		"""
		Returns the function corresponding to the task name given.
		"""

		self.task_map.setdefault(task, lambda _: print("Unrecognized command, please try again"))
		return self.task_map[task]

	def set_local(self: any, filepath: str, force: bool = True) -> None:
		"""
		Sets client to local mode with the given path as image bank.
		"""

		self.path = self._path if filepath is None else filepath
		self.encoding_map = self.encoding_map if filepath is None else self.load_images(filepath)
		if force: self._local = True

	def set_remote(self, ip: Optional[str] = None, port: Optional[int] = None, force: bool = True) -> None:
		"""
		Sets client to remote mode with the given host as image bank.
		"""

		self.ip = self.ip if ip is None else ip
		self.port = self.port if port is None else port
		if force: self._local = False

	def analyze_faces(self: any, img: np.ndarray) -> Mapping[str, List[Tuple[str, Tuple[int, int, int, int]]]]:
		"""
		Resizes the current image and classifies it to a face if possible. Local vs remote just
		specifies different locations to compare images to.
		"""

		resized: np.ndarray = cv2.resize(img, (0, 0), fx=self.scale_factor, fy=self.scale_factor)

		if self.is_local():
			return { 'matches': check_faces(resized, self.encoding_map), 'face_locations': [] }
		else:
			resp = post(f'{self.get_conn_str()}/face_recognition/detect', files={'image': img.tobytes()}, data={
						'cache': self.use_cache, 'cache_location': self.cache_location, 'shape': str(img.shape) })
			resp.raise_for_status()
			return json.loads(resp.content.decode(TEXT_ENCODING))

	def load_images(self: any) -> bool:
		"""
		Loads images from the specified path if possible, returns true if images are loaded.
		"""

		if self.is_local():
			result = local_load_images(self.path, self.encoding_map, cache=self.use_cache, cache_location=self.cache_location)
			return result is not None
		else: return False

	def load_cache(self: any) -> bool:
		"""
		Loads encodings from the specified cache directory, returns true if encodings are loaded.
		"""

		if self.is_local():
			result = local_load_cache(self.encoding_map, cache_location=self.cache_location)
			return result is not None
		else: return False
