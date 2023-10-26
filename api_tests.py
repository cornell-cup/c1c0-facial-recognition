import unittest
import os
import cv2
import sys

sys.path.insert(0, '..')

from r2_facial_recognition.client import Client

CACHE_LOCATION = '../.cache'
PATH = '../resources/people'

IP = '127.0.0.1'
PORT = 5000


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
        self.client = Client(path=PATH, ip=IP, port=PORT,
                             cache_location=CACHE_LOCATION)
        print(f'Local mode is set to {self.client.is_local()}')

    def test_local(self):
        self.client.set_local(filepath=PATH, force=True)
        for person, img in self.img_suite.items():
            print(f'Locally analyzing {person}.')
            predictions = self.client.analyze_faces(img)
            predicted = predictions['matches']
            print(f'{person} locally analyzed.')
            name, _ = predicted[0]
            self.assertEqual(name, person)

    def test_remote(self):
        self.client.set_remote(ip=IP, port=PORT, force=True)
        for person, img in self.img_suite.items():
            print(f'Remotely analyzing {person}.')
            predictions = self.client.analyze_faces(img)
            predicted = predictions['matches']
            print(f'{person} remotely analyzed.')
            name, _ = predicted[0]
            self.assertEqual(name, person)


if __name__ == '__main__':
    unittest.main()
