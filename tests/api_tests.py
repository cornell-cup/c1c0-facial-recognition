import unittest
import os
import cv2
import sys

sys.path.insert(0, '..')

from r2_facial_recognition.client import api

api.CACHE_LOCATION = '../.cache'


class APITests(unittest.TestCase):
    def setUp(self) -> None:
        files = []
        path = '../resources/test_headshots'
        for _, _, files in os.walk(path):
            files.extend(files)
        self.img_suite = {
            file[:file.rindex('.')]: cv2.imread(os.path.join(path, file))
            for file in files
        }

    def test_local(self):
        api.set_local('../resources/people')
        for person, img in self.img_suite.items():
            predicted, unknown = api.analyze_face(img)
            self.assertEqual(predicted[0], person)


if __name__ == '__main__':
    unittest.main()
