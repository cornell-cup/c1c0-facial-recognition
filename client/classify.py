import numpy as np, os, face_recognition # Default Python Libraries

from client.config import * # Default Configurations

from typing import Mapping, Tuple, List, MutableMapping # Type Hinting

# Copying Config Values
ENCODING_MODEL: str    = DEFAULT_ENCODING_MODEL
FACE_DETECT_MODEL: str = DEFAULT_NN_MODEL
UNKNOWN_FACE: str      = DEFAULT_UNKNOWN_FACE_ID
NUM_JITTERS: int       = DEFAULT_NUM_JITTERS
NUM_UPSAMPLE: int      = DEFAULT_NUM_UPSAMPLE

def check_and_add_img(img: np.ndarray, name: str, mappings: MutableMapping, cache: bool = True,
                      cache_dir: str = DEFAULT_CACHE_DIR) -> None:
    """
    Helper function that checks if the encoding is already cached for an img, and if so
    adds it to the mappings. Otherwise, it will generate an encoding for the face, and store
    it in the mappings. File names are important for it to distinguish which user is which.
    Also caches the encoding if [cache] is True and the encoding is not already cached.

    PARAMETERS
    ----------
    img       - The image as a np.ndarray.
    name      - The name of the person in the image.
    mappings  - The mappings to update with the added filenames.
    cache     - Whether to cache the files as they are loaded.
    cache_dir - The directory of the `cache` to check, default specified by `DEFAULT_CACHE_DIR`
    """

    if cache:
        try: mappings[name] = get_cached(name, cache_dir)

        except OSError:
            encodings: List[np.ndarray] = face_recognition.face_encodings(
                img, num_jitters=NUM_JITTERS, model=ENCODING_MODEL)
            if (len(encodings) == 0): print(f'No faces found in {name}.'); return

            encoding: np.ndarray = encodings[0]
            add_cache(name, encoding, cache_dir)
            mappings[name] = encoding

    else:
        encodings: List[np.ndarray] = face_recognition.face_encodings(
            img, num_jitters=NUM_JITTERS, model=ENCODING_MODEL)
        if (len(encodings) == 0): print(f'No faces found in {name}.'); return

        encoding: np.ndarray = encodings[0]
        mappings[name] = encoding

def check_and_add_file(path: str, file: str, mappings: MutableMapping, cache: bool = True,
                       cache_dir: str = DEFAULT_CACHE_DIR) -> None:
    """
    Helper function that checks if the encoding is already cached for a file, and if so
    adds it to the mappings. Otherwise, it will generate an encoding for the face, and store
    it in the mappings. File names are important for it to distinguish which user is which.
    Also caches the encoding if [cache] is True and the encoding is not already cached.

    PARAMETERS
    ----------
    path      - The path as a str to the directory where the file is located.
    file      - The filename.
    mappings  - The mappings to update with the added filenames.
    cache     - Whether to cache the files as they are loaded.
    cache_dir - The directory of the `cache` to check, default specified by `DEFAULT_CACHE_DIR`
    """

    try: filename: str = file[:file.rindex('.')]
    except ValueError as exc: raise ValueError(f'file named {file} does not contain a ".".') from exc

    if cache:
        try: mappings[filename] = get_cached(filename, cache_dir)

        except OSError:
            encodings: List[np.ndarray] = face_recognition.face_encodings(
                face_recognition.load_image_file(os.path.join(path, file)),
                num_jitters=NUM_JITTERS, model=ENCODING_MODEL)
            if (len(encodings) == 0): print(f'No faces found in {file}.'); return

            encoding: np.ndarray = encodings[0]
            add_cache(filename, encoding, cache_dir)
            mappings[filename] = encoding
    else:
        encodings: List[np.ndarray] = face_recognition.face_encodings(
            face_recognition.load_image_file(os.path.join(path, file)),
            num_jitters=NUM_JITTERS, model=ENCODING_MODEL)
        if (len(encodings) == 0): print(f'No faces found in {file}.'); return

        encoding: np.ndarray = encodings[0]
        mappings[filename] = encoding

def cload_images(path: str, mappings: Mapping[str, np.ndarray] = None, cache: bool = True,
                 cache_dir: str = DEFAULT_CACHE_DIR) -> Mapping[str, np.ndarray]:
    """
    Loads in the image(s) from the given `path` and returns an updating mappings. Only loads
    in images with the extensions specified in `IMG_EXTs`. Can handle both directories and
    individual files.

    PARAMETERS
    ----------
    path      - The path to the image or directory.
    mappings  - The mappings to update with the added filenames
    cache     - Whether to cache the files as they are loaded.
    cache_dir - The directory of the `cache` to check, default specified by `CACHE_LOCATION`

    RETURNS
    -------
    Mapping[str, np.ndarray] - A Mapping of names to encodings. The encoding is a numpy array
    representation of an individual face.
    """

    mappings: Mapping[str, np.ndarray] = {} if mappings is None else mappings

    if os.path.isdir(path):
        for _, _, files in os.walk(path):
            for file in files:
                ext: str = file[file.rindex('.')+1:]

                if ext in IMG_EXTs: check_and_add_file(path, file, mappings, cache, cache_dir)
                else: print(f'Ignoring file: {file}, with extension: {ext} not in {IMG_EXTs}')

    elif os.path.isfile(path):
        ext = path[path.rindex('.')+1:]

        if ext not in IMG_EXTs: print('File being loaded, with extension: {ext} not in {IMG_EXTs}')
        check_and_add_file(*os.path.split(path), mappings, cache, cache_dir)

    else: raise RuntimeError(f'The path given ({path}) is not a directory or file.')

    return mappings

def cload_cache(mappings: Mapping[str, np.ndarray] = None, cache_dir: str = DEFAULT_CACHE_DIR) -> Mapping[str, np.ndarray]:
    """
    Loads in the encodings from the given `path` and returns an updating mappings. Only loads
    in encodings with the extension specified in `ENCODING_EXT`. Can only handle directories.

    PARAMETERS
    ----------
    mappings  - The mappings to update with the added filenames.
    cache_dir - The directory of the `cache` to check, default specified by `CACHE_LOCATION`

    RETURNS
    -------
    Mapping[str, np.ndarray] - A Mapping of names to encodings. The encoding is a numpy array
    representation of an individual face.
    """

    mappings: Mapping[str, np.ndarray] = {} if mappings is None else mappings

    for _, _, files in os.walk(cache_dir):
        for file in files:
            ext: str = file[file.rindex('.')+1:]
            filename: str = file[:file.rindex('.')]

            if ext == ENCODING_EXT: mappings[filename] = get_cached(filename, cache_dir)
            else: print(f"Ignoring file: {file}, with extension: {ext} not equal to {ENCODING_EXT}")

    return mappings

def get_cached(name: str, cache_dir: str = DEFAULT_CACHE_DIR) -> np.ndarray:
    """
    Gets the cached encoding described by [name] from [cache_dir]. Can only handle files
    with the extension specified in `ENCODING_EXT`.

    PARAMETERS
    ----------
    name      - The name of the person whose encoding is being gotten.
    cache_dir - The path as a str of the folder where the cached encodings are located.

    RAISES
    ------
    OSError - Usually raised when the file does not exist or is unable to be accessed.

    RETURNS
    -------
    np.ndarray - The encoding as a np.ndarray.
    """

    os.makedirs(cache_dir, exist_ok=True)

    with open(os.path.join(cache_dir, f'{name}.{ENCODING_EXT}'), 'rb') as file:
        return np.frombuffer(file.read())

def add_cache(name: str, encoding: np.ndarray, cache_dir: str = DEFAULT_CACHE_DIR) -> None:
    """
    Adds the [encoding] to the [cache_dir] directory under [name]. The encoding is stored as a
    binary file with the extension specified in `ENCODING_EXT`.

    PARAMETERS
    ----------
    name      - The name of the person [encoding] is for.
    encoding  - The encoding for the person, [name].
    cache_dir - An optional argument of the directory of where the cache is located.

    RAISES
    ------
    OSError - Usually raised when the file is unable to be accessed.
    """

    os.makedirs(cache_dir, exist_ok=True)

    with open(os.path.join(cache_dir, f'{name}.{ENCODING_EXT}'), 'wb+') as file:
        file.seek(0); file.truncate(); file.write(encoding.tobytes())

def check_faces(img: np.ndarray, mappings: Mapping[str, np.ndarray]) -> List[Tuple[str, Tuple[int, int, int, int]]]:
    """
    Runs the facial recognition algorithm on [img]. All possible responses are keys in [mappings].
    Basically finds faces in images, compares to known faces in mappings, and returns a list of results
    to be used in displaying the bounding box.

    PARAMETERS
    ----------
    img      - The img to search for faces in.
    mappings - The mappings of known people to known facial encodings.

    RETURNS
    -------
    List[Tuple[str, Tuple[int, int, int, int]]] - A list of name-image location pairs. The location is in
    (top, right, bottom, left) format. Note: It is returned as a list as multiple Unknown values may be
    accrued. Any faces in the image that are recognized as a face but is not a known face will have the
    location but be marked as Unknown.
    """

    try: ordered_map: List[Tuple[str, np.ndarray]] = list(mappings.items())
    except AttributeError as exc: raise ValueError(f'Expected a Mapping. Got \'{mappings}\' instead.') from exc

    known_encodings: List[np.ndarray] = list(map(lambda x: x[1], ordered_map))
    unknown_face_locations: List[any] = face_recognition.face_locations(img,
        number_of_times_to_upsample=NUM_UPSAMPLE, model=FACE_DETECT_MODEL)
    unknown_face_encodings: List[any] = face_recognition.face_encodings(img,
        unknown_face_locations, num_jitters=NUM_JITTERS, model=ENCODING_MODEL)

    identities: List[str] = []
    for unknown_face in unknown_face_encodings:
        matches: List[bool] = face_recognition.compare_faces(known_encodings, unknown_face, tolerance=TOLERANCE)
        face_distances: np.ndarray = face_recognition.face_distance(known_encodings, unknown_face)

        idx: int = np.argmin(face_distances) if len(face_distances) > 0 else -1
        name: str = ordered_map[idx][0] if idx != -1 and matches[idx] else UNKNOWN_FACE
        identities.append(name)

    all_faces: List[Tuple[str, Tuple[int, int, int, int]]] = list(zip(identities, unknown_face_locations))
    return all_faces
