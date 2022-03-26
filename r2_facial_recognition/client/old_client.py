# This Client Program
# Voice triggered
# Get image from Pi, send it to computing server by using POST
# Receive json feedback from server 
# Make robot react to parsed json 

import requests
import picamera
import subprocess

url = "http://10.129.3.148:11000/identify-face"


def send_test_image():
    files = {
        "image": open("test.png", "rb")
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


def main():
    # capture image
    with picamera.PiCamera() as camera:
        camera.capture("test.png")
    json_feedback = send_test_image()
    person, check_in_status, meeting_type = load_json(json_feedback)
    speak_result(person, check_in_status, meeting_type)


if __name__ == '__main__':
    main()
