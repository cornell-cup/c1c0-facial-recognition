"""
Heavily drawn from https://pypi.org/project/face-recognition/
"""
import os
from typing import Mapping, Tuple, Union
from pprint import pprint

import numpy
import face_recognition

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


def _load_images(path: str, mappings: Mapping[str, numpy.ndarray] = None,
                 cache: bool = True,
                 cache_location: str = DEFAULT_CACHE_LOCATION) -> \
                 Union[Tuple[str, numpy.ndarray], Mapping[str, numpy.ndarray]]:
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
        A Mapping of names to encodings if path is a directory, a single
        Tuple of name & encoding if the path is a file, and raises an exception
        otherwise.
    """
    mappings = {} if mappings is None else mappings

    def check_and_add(path_, file_):
        try:
            filename_ = file_[:file_.rindex('.')]
        except ValueError as exc:
            raise ValueError(f'file named {file_} does not contain a ".".') \
                from exc
        if cache:
            print('Using cache.')
            # Following EAFP idiom.
            try:
                mappings[filename_] = get_cached(filename_, cache_location)
                print(f'Pulled mapping from {filename_}.')
            except OSError as exc:
                # DNE in cache
                print(exc)
                print('Couldn\'t find mapping, generating new one.')
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
        print(f'Recognized {path} as a directory.')
        for _, _, files in os.walk(path):
            print(f'Walking through files in {path}.')
            for file in files:
                print(f'Analyzing file: {file}.')
                ext_idx = file.rindex('.')
                ext = file[ext_idx+1:]
                if ext in IMG_EXTs:
                    print(f'Image extension matches: {ext}')
                    print(f'{file} was loaded in as a recognized face.')
                    # filename = file[:file.rindex('.')]
                    check_and_add(path, file)
                else:
                    print(f'Ignoring file: {file}, with extension: {ext} not '
                          f'in {IMG_EXTs}')
    elif os.path.isfile(path):
        ext_idx = path.rindex('.')
        print(path)
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


def get_cached(name: str, cache_location: str = DEFAULT_CACHE_LOCATION):
    with open(os.path.join(cache_location, f'{name}.encoding'), 'rb') as f:
        return numpy.frombuffer(f.read())


def add_cache(name: str, encoding: numpy.ndarray,
              cache_location: str = DEFAULT_CACHE_LOCATION):
    os.makedirs(cache_location, exist_ok=True)
    with open(os.path.join(cache_location, f'{name}.encoding'), 'wb+') as f:
        f.seek(0)
        f.truncate()
        f.write(encoding.tobytes())


def _check_faces(img: numpy.ndarray, mappings: Mapping[str, numpy.ndarray]):
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
    landmarks = face_recognition.face_landmarks(img, unknown_face_locations,
                                                model=ENCODING_MODEL)
    pprint(landmarks)

    identities = []
    for unknown_face in unknown_face_encodings:
        matches = face_recognition.compare_faces(known_encodings, unknown_face,
                                                 )
        face_distances = face_recognition.face_distance(known_encodings,
                                                        unknown_face)
        closest_idx = numpy.argmin(face_distances)
        distance = face_distances[closest_idx]
        name = ordered_map[closest_idx][0] if matches[closest_idx] else \
            'Unknown'
        print(f'Face was {distance} away from {name}.')

        identities.append(name)
    return identities, unknown_face_locations
