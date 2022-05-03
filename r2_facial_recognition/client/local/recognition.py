"""
Heavily drawn from https://pypi.org/project/face-recognition/

This module defines all the functions necessary to locally perform a
  facial recognition task.
"""
import os
from typing import Mapping, Tuple, List

import face_recognition
import numpy as np

try:
    from ..config import (
        DEFAULT_ENCODING_MODEL, DEFAULT_NN_MODEL, DEFAULT_CACHE_LOCATION,
        IMG_EXTs
    )
except ImportError:
    from r2_facial_recognition.client.config import (
        DEFAULT_ENCODING_MODEL, DEFAULT_NN_MODEL, DEFAULT_CACHE_LOCATION,
        IMG_EXTs
    )


ENCODING_MODEL = DEFAULT_ENCODING_MODEL
FACE_DETECT_MODEL = DEFAULT_NN_MODEL


def _load_images(path: str, mappings: Mapping[str, np.ndarray] = None,
                 cache: bool = True,
                 cache_location: str = DEFAULT_CACHE_LOCATION) -> \
                 Mapping[str, np.ndarray]:
    """
    Loads in the image(s) from the given path.

    PARAMETERS
    ----------
    path
        The path to the image or directory.
    mappings
        The mappings to update with the added filenames
    cache
        Whether to cache the files as they are loaded.
    cache_location
        The directory of the cache to check, default specified by
        CACHE_LOCATION

    RETURNS
    -------
    - Mapping[str, np.ndarray]
        A Mapping of names to encodings. The encoding is a numpy array
        representation of an individual face.
    """
    mappings = {} if mappings is None else mappings

    def check_and_add(path_: str, file_: str) -> None:
        """
        Helper function that checks if the encoding is already generated, and
        if so adds it to the mappings. Otherwise, it will generate an encoding
        for the face, and store it in the mappings. File names are important
        for it to distinguish which user is which.

        PARAMETERS
        ----------
        path_
            The path as a str to the directory where the file is located.
        file_
            The filename.
        """
        try:
            filename_ = file_[:file_.rindex('.')]
        except ValueError as exc:
            raise ValueError(f'file named {file_} does not contain a ".".') \
                from exc
        if cache:
            # Following EAFP idiom.
            try:
                mappings[filename_] = get_cached(filename_, cache_location)
            except OSError:
                # DNE in cache
                encoding = face_recognition.face_encodings(
                    face_recognition.load_image_file(os.path.join(path_,
                                                                  file_)),
                    model=ENCODING_MODEL
                )[0]
                add_cache(filename_, encoding, cache_location)
                mappings[filename_] = encoding

        else:
            mappings[filename_] = face_recognition.face_encodings(
                face_recognition.load_image_file(os.path.join(path_, file_)),
                model=ENCODING_MODEL
            )[0]

    if os.path.isdir(path):
        for _, _, files in os.walk(path):
            for file in files:
                ext_idx = file.rindex('.')
                ext = file[ext_idx+1:]
                if ext in IMG_EXTs:
                    # filename = file[:file.rindex('.')]
                    check_and_add(path, file)
                else:
                    print(f'Ignoring file: {file}, with extension: {ext} not '
                          f'in {IMG_EXTs}')
    elif os.path.isfile(path):
        ext_idx = path.rindex('.')
        if path[ext_idx+1] not in IMG_EXTs:
            print('Warning: file being explicitly loaded does not have .jpg '
                  'extension. Make sure this is actually an image file.')
        # os.path.split should return head and tail, path and filename
        # respectively
        check_and_add(*os.path.split(path))
    else:
        raise RuntimeError(f'The path given ({path}) is not a directory or '
                           f'file.')
    return mappings


def get_cached(name: str, cache_location: str = DEFAULT_CACHE_LOCATION) -> \
        np.ndarray:
    """
    Gets the cached encoding from cache_location.

    PARAMETERS
    ----------
    name
        The name of the person whose encoding is being gotten.
    cache_location
        The path as a str of the folder where the cached encodings are located.

    RETURNS
    -------
    np.ndarray
        The encoding as a np.ndarray.
    """
    with open(os.path.join(cache_location, f'{name}.encoding'), 'rb') as f:
        return np.frombuffer(f.read())


def add_cache(name: str, encoding: np.ndarray,
              cache_location: str = DEFAULT_CACHE_LOCATION) -> None:
    """
    Adds the [encoding] to the [cache_location] directory under [name].

    PARAMETERS
    ----------
    name
        The name of the person [encoding] is for.
    encoding
        The encoding for the person, [name].
    cache_location
        An optional argument of the directory of where the cache is located.
    """
    os.makedirs(cache_location, exist_ok=True)
    with open(os.path.join(cache_location, f'{name}.encoding'), 'wb+') as f:
        f.seek(0)
        f.truncate()
        f.write(encoding.tobytes())


def _check_faces(img: np.ndarray, mappings: Mapping[str, np.ndarray]) ->\
        List[Tuple[str, Tuple[int, int, int, int]]]:
    """
    Runs the facial recognition algorithm on [img]. All possible responses are
    keys in [mappings].

    PARAMETERS
    ----------
    img
        The img to search for faces in.
    mappings
        The mappings of known people to known facial encodings.
        See _load_images for more info on the mappings.

    RETURNS
    -------
    -
        A list of name-image location pairs. The location is in
        (top, right, bottom, left) format.
        |
        |
        Note: It is returned as a list as multiple Unknown values may be
        accrued. Any faces in the image that are recognized as a face but is
        not a known face will have the location but be marked as Unknown.
    """
    try:
        ordered_map = list(mappings.items())
    except AttributeError as exc:
        raise ValueError('Invalid parameter \'mapping\', expected a Mapping '
                         f'type object. Got \'{mappings}\' instead.') from exc
    known_encodings = list(map(lambda x: x[1], ordered_map))
    if not known_encodings:
        raise ValueError(f'No known encodings! known_encodings='
                         f'{known_encodings}')
    unknown_face_locations = face_recognition.face_locations(
        img, model=FACE_DETECT_MODEL)
    unknown_face_encodings = face_recognition.face_encodings(
        img, unknown_face_locations, model=ENCODING_MODEL)
    # landmarks = face_recognition.face_landmarks(img, unknown_face_locations,
    #                                             model=ENCODING_MODEL)
    # pprint(landmarks)

    identities = []
    for unknown_face in unknown_face_encodings:
        matches = face_recognition.compare_faces(known_encodings, unknown_face,
                                                 )
        face_distances = face_recognition.face_distance(known_encodings,
                                                        unknown_face)
        closest_idx = np.argmin(face_distances)
        # distance = face_distances[closest_idx]
        name = ordered_map[closest_idx][0] if matches[closest_idx] else \
            'Unknown'

        identities.append(name)
    return list(zip(identities, unknown_face_locations))
