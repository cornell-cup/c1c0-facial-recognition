from requests import get, post, HTTPError, ConnectionError
import time, threading, json, cv2, logging
import numpy as np

from client.classify import check_faces, load_images, check_and_add
from client.camera import Camera
import client.rotation as rotate
from client.config import *

from typing import Optional, List, Mapping, Tuple, Callable, Sized, Iterable

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

	def learn_face(self: any, name: str, disp: bool = False, best_of_n: int = 3, *_, **__):
		"""
		Given a name, will take a picture and create a mapping from that name to the
		approriate facial encodings.

		PARAMETERS
		----------
		name - Name of the face in the image.
		"""

		with self.camera:
			img: np.ndarray = self.camera.read()
			detected_face = check_faces(img, self.encoding_map)

			if detected_face != UNKNOWN_FACE: return

	def take_attendance(self, disp: bool = False, *_, **__) -> List[List[Tuple[str, Tuple[int, int, int, int]]]]:
		"""
		Takes a series of pictures as C1C0 turns, makes a request to the backend for each picture and unions the
		results of facial recognition. Outputs the matches and asks for confirmation from chatbot.
		"""

		res: List[List[Tuple[str, Tuple[int, int, int, int]]]] = []
		workers: List[threading.Thread] = []
		imgs: List[np.ndarray] = []
		n_imgs: int = 3

		def analyze(idx: int) -> None:
			print(f'Analyzing image {idx}.')
			results: Mapping[str, List[Tuple[str, Tuple[int, int, int, int]]]] = self.analyze_faces(np.array(imgs[idx]))
			res.append([(name, loc) for name, loc in results['matches'] if name != UNKNOWN_FACE])

		def display(img: np.ndarray, results: List[List[Tuple[str, Tuple[int, int, int, int]]]]) -> None:
			cv2.namedWindow('C1C0 Facial Recognition', cv2.WINDOW_NORMAL)
			for name, (top, right, bottom, left) in results:
				cv2.putText(img, name, (left - 20, bottom + 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

			cv2.imshow('C1C0 Facial Recognition', img)
			cv2.waitKey(1000)
			cv2.destroyAllWindows()

		def process_frame(ind: int) -> None:
			print(f'\nTaking pic {i+1}.\n')
			time.sleep(0.25)
			imgs.append(cam.read())

			workers.append(threading.Thread(target=analyze, args=(i,), daemon=True))
			workers[i].start()

		with self.camera as cam:
            # Attempting to start head rotation
			rot_time = 3
			rotate.init_serial()

			# Start processing pic 0
			process_frame(0)
			time.sleep(1)

			print('C1C0 TURN LEFT')
			time.sleep(1)
			workers[0].join()

			# Start processing pic 1
			process_frame(1)
			display(imgs[0], res[0])

			print('C1C0 TURN RIGHT')
			time.sleep(1)
			workers[1].join()

			# Start processing pic 2
			process_frame(2)
			display(imgs[1], res[1])

			time.sleep(1)
			workers[2].join()
			display(imgs[2], res[2])

		return res

	def __init__(self: any, local: 'Optional[bool]' = DEFAULT_LOCAL, path: str = DEFAULT_PATH,
				 cache: bool = DEFAULT_CACHE, cache_location: str = DEFAULT_CACHE_LOCATION,
                 mappings = None, ip = DEFAULT_HOST, port = DEFAULT_PORT, dev: str = DEFAULT_DEVICE,
				 scale_factor: float = DEFAULT_SCALE_FACTOR, timeout: float = DEFAULT_TIMEOUT,
                 check_in_rate: float = DEFAULT_CHECKIN_RATE) -> 'Client':
		"""
		Initializes an instance of client with a lot of default values and configurations.
		"""

		self.camera = Camera(dev)
		# self.task_map = { 'learn_face': self.learn_face, 'take_attendance': self.take_attendance }
		# self.local = local
		# self.path = path
		# self.use_cache = cache
		# self.cache_location = cache_location
		# self.encoding_map = mappings if mappings is not None else {}
		# self.ip = ip
		# self.port = port
		# self.scale_factor = DEFAULT_SCALE_FACTOR if scale_factor is None else scale_factor
		# self.timeout = timeout
		# self.last_result = (False, 0)
		# self.check_in_rate = check_in_rate
		# self.load_images()

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

		return self.task_map[task]

	def set_local(self: any, filepath: str, force: bool = True) -> None:
		"""
		Sets client to local mode with the given path as image bank.
		"""

		self.path = self._path if filepath is None else filepath
		self.encoding_map = self.encoding_map if filepath is None else load_images(filepath)
		if force: self._local = True

	def set_remote(self, ip: Optional[str] = None, port: Optional[int] = None, force: bool = True) -> None:
		"""
		Sets client to remote mode with the given host as image bank.
		"""

		self.ip = self.ip if ip is None else ip
		self.port = self.port if port is None else port
		if force: self._local = False

	def set_auto(self: any) -> None:
		"""
		Sets client to neither mode, so it can auto assume whenever a function is running.
		"""

		self.local = None

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
		Loads images from the specified cache directory is possible, returns the result
		of loading those images.
		"""

		if self.is_local():
			result = load_images(self.path, self.encoding_map, cache=self.use_cache, cache_location=self.cache_location)
			return result
		else: return True

	def add_face(self: any, img: np.ndarray) -> None:
		"""
		Adds a face encoding if possible.
		"""

		if self.is_local(): check_and_add()

	def get_actions(self: any) -> List[str]:
		"""
		Returns the list of possible actions for the client.
		"""

		return list(self._task_map.keys())
