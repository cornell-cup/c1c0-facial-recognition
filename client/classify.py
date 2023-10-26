import os, face_recognition
import numpy as np

from client.config import *

from typing import Mapping, Tuple, List, MutableMapping

# Configurations
ENCODING_MODEL: str = DEFAULT_ENCODING_MODEL
FACE_DETECT_MODEL: str = DEFAULT_NN_MODEL
UNKNOWN_FACE: str = DEFAULT_UNKNOWN_FACE_ID

def check_and_add(path: str, file: str, mappings: MutableMapping, cache_location: str = DEFAULT_CACHE_LOCATION, cache: bool = True) -> None:
	"""
	Helper function that checks if the encoding is already generated, and if so adds it to
	the mappings. Otherwise, it will generate an encoding for the face, and store it in
	the mappings. File names are important for it to distinguish which user is which.

    PARAMETERS
    ----------
    path - The path as a str to the directory where the file is located.
    file - The filename.
    """

	try: filename: str = file[:file.rindex('.')]
	except ValueError as exc:
		raise ValueError(f'file named {file_} does not contain a ".".') from exc

	if cache:
		# Following EAFP idiom.
		try: mappings[filename] = get_cached(filename, cache_location)
		except OSError:
			# DNE in cache
			encodings: List[np.ndarray] = face_recognition.face_encodings(
				face_recognition.load_image_file(os.path.join(path, file)),
				model=ENCODING_MODEL
			)

			encoding: np.ndarray = encodings[0]
			add_cache(filename, encoding, cache_location)
			mappings[filename] = encoding

	else:
		encodings: List[np.ndarray] = face_recognition.face_encodings(
			face_recognition.load_image_file(os.path.join(path_, file_)),
			model=ENCODING_MODEL
        )

		encoding: np.ndarray = encodings[0]
		mappings[filename] = encoding

def load_images(path: str, mappings: Mapping[str, np.ndarray] = None, cache: bool = True,
	cache_location: str = DEFAULT_CACHE_LOCATION) -> Mapping[str, np.ndarray]:
	"""
	Loads in the image(s) from the given `path`.

	PARAMETERS
	----------
	path - The path to the image or directory.
	mappings - The mappings to update with the added filenames
	cache - Whether to cache the files as they are loaded.
	cache_location - The directory of the `cache` to check, default specified by `CACHE_LOCATION`

	RETURNS
	-------
	A Mapping of names to encodings. The encoding is a numpy array representation of an
	individual face.
	"""

	mappings: Mapping[str, np.ndarray] = {} if mappings is None else mappings

	if os.path.isdir(path):
		for _, _, files in os.walk(path):
			for file in files:
				ext = file[file.rindex('.')+1:]

				if ext in IMG_EXTs: check_and_add(path, file, mappings, cache_location, cache)
				else: print(f'Ignoring file: {file}, with extension: {ext} not in {IMG_EXTs}')

	elif os.path.isfile(path):
		ext = path[path.rindex('.')+1:]

		if ext not in IMG_EXTs: print('File being loaded, with extension: {ext} not in {IMG_EXTs}')
		check_and_add(*os.path.split(path), mappings, cache_location, cache)

	else: raise RuntimeError(f'The path given ({path}) is not a directory or file.')

	return mappings

def get_cached(name: str, cache_location: str = DEFAULT_CACHE_LOCATION) -> np.ndarray:
	"""
	Gets the cached encoding from cache_location.

	PARAMETERS
	----------
	name - The name of the person whose encoding is being gotten.
	cache_location - The path as a str of the folder where the cached encodings are located.

	RAISES
	------
	OSError - Usually raised when the file does not exist or is unable to be accessed.

	RETURNS
	-------
	np.ndarray - The encoding as a np.ndarray.
	"""

	with open(os.path.join(cache_location, f'{name}.encoding'), 'rb') as file:
		return np.frombuffer(file.read())

def add_cache(name: str, encoding: np.ndarray, cache_location: str = DEFAULT_CACHE_LOCATION) -> None:
	"""
	Adds the [encoding] to the [cache_location] directory under [name].

	PARAMETERS
	----------
	name - The name of the person [encoding] is for.
	encoding - The encoding for the person, [name].
	cache_location - An optional argument of the directory of where the cache is located.
	"""
	os.makedirs(cache_location, exist_ok=True)

	with open(os.path.join(cache_location, f'{name}.encoding'), 'wb+') as f:
		f.seek(0); f.truncate()
		f.write(encoding.tobytes())

def check_faces(img: np.ndarray, mappings: Mapping[str, np.ndarray]) -> List[Tuple[str, Tuple[int, int, int, int]]]:
	"""
	Runs the facial recognition algorithm on [img]. All possible responses are keys in [mappings].

	PARAMETERS
	----------
	img - The img to search for faces in.
	mappings - The mappings of known people to known facial encodings. See load_images for more info on the mappings.

	RETURNS
	-------
	A list of name-image location pairs. The location is in (top, right, bottom, left) format. Note: It is returned
	as a list as multiple Unknown values may be accrued. Any faces in the image that are recognized as a face but
	is not a known face will have the location but be marked as Unknown.
	"""

	try: ordered_map: List[Tuple[str, np.ndarray]] = list(mappings.items())
	except AttributeError as exc: raise ValueError(f'Expected a Mapping type object. Got \'{mappings}\' instead.') from exc

	known_encodings: List[np.ndarray] = list(map(lambda x: x[1], ordered_map))
	if not known_encodings: raise ValueError(f'No known encodings! known_encodings = {known_encodings}')

	unknown_face_locations: List[any] = face_recognition.face_locations(img, model=FACE_DETECT_MODEL)
	unknown_face_encodings: List[any] = face_recognition.face_encodings(img, unknown_face_locations, model=ENCODING_MODEL)

	identities: List[str] = []
	for unknown_face in unknown_face_encodings:
		matches: List[bool] = face_recognition.compare_faces(known_encodings, unknown_face)
		face_distances: np.ndarray = face_recognition.face_distance(known_encodings, unknown_face)

		closest_idx: int = np.argmin(face_distances)
		name: str = ordered_map[closest_idx][0] if matches[closest_idx] else UNKNOWN_FACE
		identities.append(name)

	all_faces: List[Tuple[str, Tuple[int, int, int, int]]] = list(zip(identities, unknown_face_locations))
	return all_faces
