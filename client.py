import json
import requests
import sys
import io
import socket
import picamera
import atexit
import time
import base64
from PIL import Image

url = "http://127.0.0.1:5000/analyze"

# send the image (locally named "test.png") from the Pi camera 
# to the url on server, and return the json feedback
def send_test_image():
    files = {
        "image": open("test.png", "rb")
    }
    response = requests.post(url, files=files, verify=False)
    return response

# get the check in result from the json and return the reuslt
def JsonLoad(CheckInData):
   temp = json.load(CheckInData)

   person = temp[name]
   CurrentTime = temp[CurrentTime]
   Status = temp[Status]
   MeetingType = temp[MeetingType]
   return person, CurrentTime, Status, MeetingType

# speak the check in result using, to be implemented
# we just print it to the console here
def speakResult(person, CurrentTime, Status, MeetingType):
	print(person)
	print(CurrentTime)
	print(Status)
	print(MeetingType)

def main():
	# capture image
    with picamera.PiCamera() as camera:
        camera.capture("test.png")
    json_feedback = send_test_image()
    person, CurrentTime, Status, MeetingType = JsonLoad(json_feedback)
    speakResult(person, CurrentTime, Status, MeetingType)

main()
