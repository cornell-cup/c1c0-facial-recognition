import numpy as np, time, cv2 # Default Python Libraries

from client.classify import check_faces, cload_images # Classification Functions
from client.classify import cload_cache, check_and_add_img # Caching Functions
from client.camera import Camera # Class For Activating The Camera
from client.config import * # Default Configuration Values

from typing import List, Mapping, Tuple, Set # Type Hinting

# Copying Config Values
UNKNOWN_FACE: str = DEFAULT_UNKNOWN_FACE_ID

class Client:
    """
    Class representing the main bulk of the facial recognition client. Used to classify
    images, store encodings of faces, and return names of people recognized in images.
    """

    def display(self: any, img: np.ndarray, results: List[Tuple[str, Tuple[int, int, int, int]]]) -> None:
        """
        Displays the image with bounding boxes around the faces and the names of the people
        recognized in the image.

        PARAMETERS
        ----------
        img     - The image to display.
        results - The results of the facial recognition.
        """

        for i, (name, (top, right, bottom, left)) in enumerate(results):
            top = int(top / self.scale_factor);       right = int(right / self.scale_factor)
            bottom = int(bottom / self.scale_factor); left = int(left / self.scale_factor)
            color: Tuple[int, int, int] = COLORS[i % len(COLORS)];

            cv2.rectangle(img, (left, top), (right, bottom), color, 2)
            cv2.putText(img, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, color, 2)

        WINDOW_NAME: str = 'Recognized Faces: Frame ' + str(self.face_number);
        cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_AUTOSIZE); self.face_number += 1
        cv2.imshow(WINDOW_NAME, img); cv2.waitKey(0)
        cv2.waitKey(1); cv2.destroyWindow(WINDOW_NAME); cv2.waitKey(1)

    def classify_image(self: any, file: str, disp: bool = True, prnt: bool = True) -> List[str]:
        """
        Given a file, will classify the images and return a list of names of people recognized
        in the image. Also displays the image with bounding boxes if disp is true, and prints
        intermediate results if prnt is true.

        PARAMETERS
        ----------
        file  - The file to classify.
        disp  - Whether or not to display the image with bounding boxes.
        prnt  - Whether or not to print the intermediate results.

        RETURNS
        -------
        List[str] - The names of the people recognized in the image.
        """

        try:
            img: np.ndarray = cv2.imread(file)

            if (prnt): print(f'Analyzing image: {img[0][0]}, {img[0][1]}, {img[0][2]}, ...')
            results: any = self.analyze_faces(img)['matches']
            pruned: any = [(name, loc) for name, loc in results if name != UNKNOWN_FACE]

            if (disp): self.display(img, results)

        except: raise OSError(f'File {file} does not exist.')

        names: Set[str] = {name for name, _ in pruned}
        formatted: str = "[" + ", ".join(names) + "]"
        if (prnt): print(f"Recognized: {formatted}");
        return names

    def learn_face(self: any, names: List[str], disp: bool = True, prnt: bool = True) -> List[str]:
        """
        Given a name, will take a picture and create a mapping from that name to the
        approriate facial encodings. Also displays the image with bounding boxes if
        disp is true, and prints intermediate results if prnt is true.

        PARAMETERS
        ----------
        name - Name of the face in the image.
        disp - Whether or not to display the image with bounding boxes.
        prnt - Whether or not to print the intermediate results.

        RETURNS
        -------
        List[str] - The names of the people recognized in the image.
        """

        name = ' '.join(names) if len(names) > 0 else "Face Num " + str(self.face_number)

        if (prnt): print('Taking picture and starting analyzation process.')
        img: np.ndarray = self.camera.adjust_read() if self.open else self.image

        if (prnt): print(f'Analyzing image: {img[0][0]}, {img[0][1]}, {img[0][2]}, ...')
        check_and_add_img(img, name, self.encoding_map, cache=self.cache, cache_dir=self.cache_dir)
        results: any = self.analyze_faces(img)['matches']
        pruned: any = [(name, loc) for name, loc in results if name != UNKNOWN_FACE]

        if (disp): self.display(img, results)

        names: Set[str] = {name for name, _ in pruned}
        formatted: str = "[" + ", ".join(names) + "]"
        if (prnt): print(f"Recognized: {formatted}");
        return names

    def take_attendance(self: any, disp: bool = True, prnt: bool = True) -> List[str]:
        """
        Takes a picture and returns a list of names of people recognized in the image.
        Also displays the image with bounding boxes if disp is true, and prints intermediate
        results if prnt is true.

        PARAMETERS
        ----------
        disp - Whether or not to display the image with bounding boxes.
        prnt - Whether or not to print the intermediate results.

        RETURNS
        -------
        List[str] - The names of the people recognized in the image.
        """

        if (prnt): print('Taking picture and starting analyzation process.')
        img: np.ndarray = self.camera.adjust_read() if self.open else self.image

        if (prnt): print(f'Analyzing image: {img[0][0]}, {img[0][1]}, {img[0][2]}, ...')
        results: any = self.analyze_faces(img)['matches']
        pruned: any = [(name, loc) for name, loc in results if name != UNKNOWN_FACE]

        if (disp): self.display(img, results)

        names: Set[str] = {name for name, _ in pruned}
        formatted: str = "[" + ", ".join(names) + "]"
        if (prnt): print(f"Recognized: {formatted}");
        return names

    def __init__(self: any, path: str = DEFAULT_PATH, open: bool = DEFAULT_OPEN, load: bool = DEFAULT_LOAD,
                 disp: bool = DEFAULT_DISP, prnt: bool = DEFAULT_PRINT, cache: bool = DEFAULT_CACHE,
                 cache_dir: str = DEFAULT_CACHE_DIR, mappings = None, camera: str = DEFAULT_CAMERA,
                 scale_factor: float = DEFAULT_SCALE_FACTOR,) -> 'Client':
        """
        Initializes an instance of client with a lot of default values and configurations.

        PARAMETERS
        ----------
        path         - The path to the directory containing the images to load.
        open         - Whether or not to open the camera.
        load         - Whether or not to load images from the specified path.
        disp         - Whether or not to display the image with bounding boxes.
        prnt         - Whether or not to print the results of the facial recognition.
        cache        - Whether or not to load encodings from the specified cache directory.
        cache_dir    - The directory to load encodings from.
        mappings     - The mappings to update with the added filenames.
        camera       - The camera to use.
        scale_factor - The scale factor to use when resizing images.
        """

        self.open = open; self.path: str = path; self.load: bool = load;
        self.disp: bool = disp; self.prnt: bool = prnt
        self.camera = Camera(camera) if self.open else None
        self.image: np.ndarray = None;
        self.cache: bool = cache; self.cache_dir: str = cache_dir
        self.face_number: int = 0; self.stall: float = 0.5
        self.encoding_map = mappings if mappings is not None else {}
        self.scale_factor = DEFAULT_SCALE_FACTOR if scale_factor is None else scale_factor

        self.task_map = {
            'classify': (lambda files: self.classify_image(files[0], disp=disp, prnt=prnt)),
            'c': (lambda files: self.classify_image(files[0], disp=disp, prnt=prnt)),

            'learn': (lambda names: self.learn_face(names, disp=disp, prnt=prnt)),
            'l': (lambda names: self.learn_face(names, disp=disp, prnt=prnt)),

            'attendance': (lambda _: self.take_attendance(disp=disp, prnt=prnt)),
            'a': (lambda _: self.take_attendance(disp=disp, prnt=prnt)),
        }

        if (load): self.load_images()
        if (cache): self.load_cache()

    def interpret_task(self: any, task: str) -> any:
        """
        Returns the function corresponding to the task name given.

        PARAMETERS
        ----------
        task - The task to interpret.

        RETURNS
        -------
        any - The function corresponding to the task name given.
        """

        self.task_map.setdefault(task, lambda _: print("Unrecognized command, please try again"))
        return self.task_map[task]

    def analyze_faces(self: any, img: np.ndarray) -> Mapping[str, List[Tuple[str, Tuple[int, int, int, int]]]]:
        """
        Resizes the current image and classifies it to a face if possible.

        PARAMETERS
        ----------
        img - The image to classify.

        RETURNS
        -------
        Mapping[str, List[Tuple[str, Tuple[int, int, int, int]]]] - A mapping from the name of the face to the
        list of locations of the faces in the image.
        """

        resized: np.ndarray = cv2.resize(img, (0, 0), fx=self.scale_factor, fy=self.scale_factor)
        return { 'matches': check_faces(resized, self.encoding_map), 'face_locations': [] }

    def load_images(self: any) -> bool:
        """
        Loads images from the specified path if possible, returns true if images are loaded.

        RETURNS
        -------
        bool - True if images are loaded, false otherwise.
        """

        result = cload_images(self.path, self.encoding_map, cache=self.cache, cache_dir=self.cache_dir)
        return result is not None

    def load_cache(self: any) -> bool:
        """
        Loads encodings from the specified cache directory, returns true if encodings are loaded.

        RETURNS
        -------
        bool - True if encodings are loaded, false otherwise.
        """

        result = cload_cache(self.encoding_map, cache_dir=self.cache_dir)
        return result is not None
