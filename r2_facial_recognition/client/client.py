# This Client Program
# Voice triggered
# Get image from Pi, send it to computing server by using POST
# Receive json feedback from server
# Make robot react to parsed json

import requests
import picamera
import face_recognition
from PIL import Image
import subprocess


# find largest face in the image
# return None if no face is found or the face is too small
# (less than 1/12 of the image)
def find_face(image):
    face_locations = face_recognition.face_locations(image)
    """
    for face_location in face_locations:
        top, right, bottom, left = face_location
        image_x, image_y, d = image.shape
        # minimal threshold to reject a face result if face too small
        threshold = min(image_x, image_y) / 12
        if right - left > threshold:
            # a qualifying face
            return face_location
    """
    if len(face_locations) > 0:
        return face_locations[0]

    return None


url = "http://10.129.2.193:11000/identify-face"


def send_test_image():
    files = {
        "image": open("cropped.png", "rb")
    }
    response = requests.post(url, files=files, verify=False)
    return response.json()


# get the check in result from the json and return the reuslt
def load_json(check_in_data):
    # temp = json.load(CheckInData)
    temp = check_in_data
    person = temp['name']
    check_in_status = temp['check_in_status']
    meeting_type = temp['meeting_type']
    return person, check_in_status, meeting_type


# speak the check in result using
def speak_result(person, check_in_status, meeting_type):
    print(person)
    if person == 'None':
        text = 'No such a person'
    if person is None:
        text = 'No such a person and person is none'
    else:
        text = person + 'successfully check in'
    subprocess.check_output(['espeak', '-ven-us', text])


def detect_face():
    # capture image
    failure_tries = 0
    camera = picamera.PiCamera()
    camera.resolution = (960, 540)
    while failure_tries < 3:
        image = camera.capture("capture.png")
        image = face_recognition.load_image_file("capture.png")
        face_location = find_face(image)
        if face_location is not None:
            top, right, bottom, left = face_location
            # check if the face is within the middle 20% of the image
            face_center = (right + left) / 2
            image_x, image_y, d = image.shape
            if image_y * 0.3 < face_center < image_y * 0.7:
                # crop image

                top = top - min(50, bottom)
                bottom = bottom + min(50, image_x - top)
                left = left - min(50, left)
                right = right + min(50, image_y - right)

                face_image = image[top:bottom, left:right]
                pil_image = Image.fromarray(face_image)
                pil_image.save('cropped.png', 'PNG')
                print("cropped")
                return True
        else:
            # shake head and say i cannot find you
            failure_tries += 1
    return False


def write_result_to_file(json_feedback):
    with open('facial_recognition_result.txt', 'wb') as f:
        f.write(json_feedback + '\n')


def check_in():
    # detected a valid face
    if detect_face():
        print("detected a valid face")
        json_feedback = send_test_image()
        person, check_in_status, meeting_type = load_json(json_feedback)
        print(person, check_in_status, meeting_type)
        # speakResult(person, check_in_status, meeting_type)
        write_result_to_file(json_feedback)

    else:
        print("cannot detect a valid face")


# name should be the parameter to be passed in
def make_friend(name):
    if detect_face():
        print("detected a valid face")
        # json_feedback = send_test_image()
        # TODO to send a new image along with name

    else:
        print("cannot detect a valid face")


if __name__ == '__main__':
    check_in()
