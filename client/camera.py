import numpy as np, threading, time, cv2

from client.config import DEFAULT_CAMERA

from typing import List, Optional

class Camera:
    """
    A wrapper around cv2.VideoCapture, see https://docs.opencv.org/3.4/d8/dfe/classcv_1_1VideoCapture.html
    """

    def __init__(self: any, camera: Optional[int] = DEFAULT_CAMERA, attempts: int = 30) -> None:
        """
        Facial recognition camera initialization

        PARAMETERS
        ----------
        camera   - The camera device to attempt first.
        attempts - The number of attempts to try to read in frames from the camera.
        """

        self.devices: int                = 10
        self.attempts: int               = attempts
        self.image: Optional[np.ndarray] = None

        self.camera: str                 = self.find_camera() if camera is None else camera
        self.device: cv2.VideoCapture    = cv2.VideoCapture(self.camera, cv2.CAP_GSTREAMER)

    def __enter__(self: any) -> None:
        """
        Initializer for when doing 'with Camera as cam' or something similar.
        """

        if not self.device.isOpened():
            if not self.device.open(self.camera):
                raise OSError(f'Unable to open device at index: {self.camera}')

        self.reader: threading.Thread = threading.Thread(target=self.read_image)
        if not self.reader.is_alive(): self.reader.start()
        return self

    def __exit__(self: any, exc_type: any, exc_val: any, exc_tb: any) -> None:
        """
        Exit process for whenever main thread wants to reconnect with child.
        """

        if self.reader.is_alive(): self.reader.join()
        self.device.release()

    def adjust_read(self: any, sat_mod: int = -10, brightness_mod: int = 10, timeout: int = 10) -> np.ndarray:
        """
        Repeatedly tries to adjust the brightness and saturdation of the current read image.
        Sourced from the following: https://stackoverflow.com/questions/32609098/how-to-fast-change-image-brightness-with-python-opencv

        PARAMETERS
        ----------
        img             - The image to adjust, in BGR format.
        sat_mod         - The saturation modifier, more positive is more saturated.
        brightness_mod  - The brightness modifier, more positive is brighter.

        RETURNS
        -------
        np.ndarray - The adjusted image, in BGR format.
        """

        ind: int = 0
        while ind < timeout:
            try:
                hsv: np.ndarray = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)

                result: np.ndarray = np.array(hsv, dtype=hsv.dtype)
                result[:, :, 1] = cv2.add(hsv[:,:,1], sat_mod)
                result[:, :, 2] = cv2.add(hsv[:,:,2], brightness_mod)

                rgb: np.ndarray = cv2.cvtColor(result, cv2.COLOR_HSV2BGR)
                return rgb

            except cv2.error: ind += 1; time.sleep(1); continue

        raise OSError(f'Unable to adjust image after {timeout} attempts.')

    def read_image(self: any, attempts: Optional[int] = None) -> None:
        """
        Attempts to read in frames from camera until success.

        PARAMETERS
        ----------
        attempts - The number of attempts to try to read in frames from the camera.
        """

        attempts: int = self.attempts if attempts is None else attempts
        fnd: bool = False

        for _ in range(attempts):
            ret: bool; img: np.ndarray; ret, img = self.device.read()

            if ret: self.image: np.ndarray = img; fnd: bool = True
            time.sleep(0.1)

        if not fnd: raise OSError(f'No frames received after {attempts} attempts.')

    def find_camera(self: any, rgb: bool = True, devices: Optional[int] = None, attempts: Optional[int] = None) -> int:
        """
        Attempts to initalize cameras and returns descriptor of first working one.

        PARAMETERS
        ----------
        rgb      - Whether or not to only return RGB cameras.
        devices  - The number of devices to try to initialize.
        attempts - The number of attempts to try to read in frames from the camera.

        RETURNS
        -------
        int - The descriptor of the first working camera.
        """

        camera:   int = 0
        devices:  int = self.devices if devices is None else devices
        attempts: int = self.attempts if attempts is None else attempts

        while camera < devices:
            cam: cv2.VideoCapture = cv2.VideoCapture(camera)
            if not cam.isOpened(): camera += 1; continue

            attempt: int = 0
            ret: bool    = False

            try:
                img: Optional[np.ndarray] = None

                while not ret:
                    ret: bool; img: np.ndarray; ret, img = cam.read()

                    if attempt >= attempts: raise RuntimeError(f'No frames received after {attempts} tries.')
                    attempt += 1

                if rgb and img is not None and not Camera.is_rgb(img):
                    raise RuntimeError(f'Camera {camera} is not RGB.')

                cam.release(); return camera

            except RuntimeError:
                cam.release(); camera += 1; continue

        raise RuntimeError('No valid camera device found.')

    def is_rgb(img: np.ndarray, sampling: int = 5) -> bool:
        """
        Determines whether a certain camera is RGB or not.

        PARAMETERS
        ----------
        img      - The image to check.
        sampling - The number of pixels to sample.

        RETURNS
        -------
        bool - Whether or not the image is RGB.
        """

        try:
            width: int; height: int; width, height, _ = img.shape
        except ValueError:
            width: int; height: int; width, height = img.shape

        for x in range(sampling):
            for y in range(sampling):
                try:
                    scaled_x: int = int((x / sampling) * width)
                    scaled_y: int = int((y / sampling) * height)
                    pixel: List[float] = img[scaled_x, scaled_y]

                    if pixel[0] != pixel[1] or pixel[1] != pixel[2]: return True

                except IndexError: continue

        return False
