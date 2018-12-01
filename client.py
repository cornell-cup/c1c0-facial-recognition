# This Client Program
# Voice triggered
# Get image from Pi, send it to computing server by using POST
# Receive json feedback from server 
# Make robot react to parsed json 

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

url = "http://10.129.20.104:11000/identify-face"

def send_test_image():
    files = {
        "image": open("test.png", "rb")
    }
    response = requests.post(url, files=files, verify=False)
    return response.json()

#get the check in result from the json and return the reuslt
def JsonLoad(CheckInData):
    #temp = json.load(CheckInData)
    temp = CheckInData
    person = temp['name']
    checkInStatus = temp['checkInStatus']
    meetingType = temp['meetingType']
    return person, checkInStatus, meetingType


#speak the check in result using
def speakResult(person, checkInStatus, meetingType):
	print(person)
	print(checkInStatus)
	print(meetingType)

def main():
	# capture image
    with picamera.PiCamera() as camera:
        camera.capture("test.png")
    json_feedback = send_test_image()
    person, checkInStatus, meetingType = JsonLoad(json_feedback)
    speakResult(person, checkInStatus, meetingType)

main()
