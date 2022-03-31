__all__ = ['load_images', 'check_faces']

try:
    from .recognition import load_images, check_faces
except ImportError:
    from r2_facial_recognition.client.local.recognition import (
        load_images, check_faces
    )
