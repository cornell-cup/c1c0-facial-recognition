"""
Imports local_load_images and local_check_faces for use elsewhere.
"""

__all__ = ['local_load_images', 'local_check_faces']

try:
    from .recognition import (
        _load_images as local_load_images, _check_faces as local_check_faces
    )
except ImportError:
    from r2_facial_recognition.client.local.recognition import (
        _load_images as local_load_images, _check_faces as local_check_faces
    )
