from client.config import DEFAULT_DEVICE, LOG_LEVEL, LOG_FILE
import logging, threading, time, cv2
import numpy as np

from typing import Optional

# Custom error for device failure.
class DeviceError(OSError): pass

class Camera:
	"""
	A wrapper around cv2.VideoCapture, see https://docs.opencv.org/3.4/d8/dfe/classcv_1_1VideoCapture.html
	"""

	dev: cv2.VideoCapture

	def __init__(self: any, dev: Optional[int] = DEFAULT_DEVICE, n_tries: int = 30) -> 'Camera':
		"""
		Facial recognition camera initialization

		PARAMETERS
		----------
		dev - Device ID for the camera. Refer to cv2.VideoCapture. If None, will call
        	  Camera.find_camera() to get the camera. By default will use the config
              value, DEFAULT_DEVICE.
        """

		self._dev: str = Camera.find_camera() if dev is None else dev
		self.dev: cv2.VideoCapture = cv2.VideoCapture(self._dev, cv2.CAP_GSTREAMER)
		self.n_tries: int = n_tries
		self.current_img: Optional[np.ndarray] = None

	def __enter__(self: any) -> 'Camera':
		"""
		Initializer for when doing 'with Camera as cam' or something similar.
		"""

		if not self.dev.isOpened():
			if not self.dev.open(self._dev):
				raise DeviceError(f'Unable to open device at index: {self._dev}')

		self.reader: Thread = threading.Thread(target=self.read_image)
		if not self.reader.is_alive(): self.reader.start()
		return self

	def __exit__(self: any, exc_type: any, exc_val: any, exc_tb: any) -> 'Camera':
		"""
		Exit process for whenever main thread wants to reconnect with child.
		"""

		if self.reader.is_alive(): self.reader.join()
		self.dev.release()

	def adjust_read(self: any, timeout: int = 5) -> None:
		"""
		Repeatedly tries to adjust the brightness of the current read image.
		"""

		ind: int = 0
		while ind < timeout:
			try: return Camera.adjust_hsv(self.current_img)
			except cv2.error: ind += 1; time.sleep(1)

	@staticmethod
	def adjust_hsv(img: np.ndarray, sat_mod: int = -70, brightness_mod: int = 60) -> np.ndarray:
		"""
		Utility for adjusting the brightness of an image. Sourced from the following:
        https://stackoverflow.com/questions/32609098/how-to-fast-change-image-brightness-with-python-opencv
		"""

		hsv: np.ndarray = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

		result: np.ndarray = np.array(hsv, dtype=hsv.dtype)
		result[:, :, 1] = cv2.add(hsv[:,:,1], sat_mod)
		result[:, :, 2] = cv2.add(hsv[:,:,2], brightness_mod)

		rgb: np.ndarray = cv2.cvtColor(result, cv2.COLOR_HSV2BGR)
		return rgb

	def read_image(self: any, n_tries: Optional[int] = None) -> None:
		"""
		Attempts to read in frames from camera until success.
		"""

		n_tries: int = self.n_tries if n_tries is None else n_tries
		fnd: bool = False
		for _ in range(n_tries):
			ret: bool; img: np.ndarray
			ret, img = self.dev.read()
			if ret:
				self.current_img: np.ndarray = img
				fnd: bool = True
			time.sleep(0.1)
		if not fnd: raise DeviceError(f'No frames received after {n_tries} tries.')

	@staticmethod
	def find_camera(rgb_only: bool = True, n_devices: int = 10, n_tries: int = 30) -> int:
		"""
		Attempts to initalize cameras and returns descriptor of first working one.
		"""

		_dev: int = 0

		while _dev < n_devices:
			cam: cv2.VideoCapture = cv2.VideoCapture(_dev)
			if not cam.isOpened():_dev += 1; continue

			tries: int = 0
			ret: bool = False

			try:
				img: Optional[np.ndarray] = None

				while not ret:
					ret: bool; img: np.ndarray
					ret, img = cam.read()
					if tries >= n_tries: raise RuntimeError(f'No frames received after {n_tries} tries.')
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
	def is_rgb(img: np.ndarray, sampling: int = 5) -> bool:
		"""
		Determines whether a certain camera is RGB or not.
		"""

		try:
			width: int; height: int
			width, height, _ = img.shape
		except ValueError:
			width: int; height: int
			width, height = img.shape

		for x in range(sampling):
			for y in range(sampling):
				try:
					scaled_x: int = int((x / sampling) * width)
					scaled_y: int = int((y / sampling) * height)
					pixel: List[float] = img[scaled_x, scaled_y]

					if pixel[0] != pixel[1] or pixel[1] != pixel[2]: return True

				except IndexError: continue

		return False
