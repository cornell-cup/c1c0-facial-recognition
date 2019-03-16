import json
import requests
import sys
import io
import socket
import picamera
import face_recognition
from PIL import Image

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

url = "http://10.129.3.148:11000/identify-face"

def send_test_image():
    files = {
        "image": open("cropped.png", "rb")
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
    if person == 'None':
        text = 'No such a person'
    if person == None:
        text = 'No such a person and person is none'
    else:
        text = person + 'successfully check in'
    subprocess.check_output(['espeak','-ven-us', text])
    
# detect face with capture_continuous function
# faster capture by using the video port

def DetectFace():

    failure_tries = 0
	with picamera.PiCamera() as camera:
		for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
			image = frame.array
        	face_location = find_face(image)
        	if face_location != None:
            top, right, bottom, left = face_location
            # check if the face is within the middle 20% of the image
            face_center = (right + left) / 2
            image_x, image_y, d = image.shape
            if face_center > image_y * 0.3 and face_center < image_y * 0.7:
                # crop image
                face_image = image[top:bottom, left:right]
                pil_image = Image.fromarray(face_image)
                pil_image.save('cropped.png', 'PNG')
                print("cropped")
                return True
			if failure_tries > 5:
				# cannot find any face in the photo
				break
			failure_tries += 1
        
    return False
            
def CheckIn():
    # detected a valid face
    if DetectFace():
        print("detected a valid face")  
        json_feedback = send_test_image()
        person, checkInStatus, meetingType = JsonLoad(json_feedback)
        speakResult(person, checkInStatus, meetingType)
        
    else:
        print("cannot detect a valid face") 
    
# name should be the parameter to be passed in
def MakeFriend(name):
    
    if DetectFace():
        print("detected a valid face")  
        # json_feedback = send_test_image()
        # TODO to send a new image along with name
        
    else:
        print("cannot detect a valid face") 
