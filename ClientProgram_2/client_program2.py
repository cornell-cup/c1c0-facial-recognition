#This Client Program 2 (Always Listening) receive JSON from Buffer program and record sign-in status.
#It also speak out with the result.
import json
import requests
import sys

API_ENDPOINT_CheckInData = ""

def get_request_checkInData():
    try:
        r = requests.get(API_ENDPOINT_CheckInData)
        CheckInData = r.json()
        r.raise_for_status()
        return CheckInData
    except requests.exceptions.RequestException as err:
        print(err)
        sys.exit(1)


#get the check in result from the json and return the reuslt
def JsonLoad(CheckInData):
   temp = json.load(CheckInData)

   person = temp[name]
   CurrentTime = temp[CurrentTime]
   Status = temp[Status]
   MeetingType = temp[MeetingType]
   return person, CurrentTime, Status, MeetingType


#speak the check in result using
def speakResult(person, CurrentTime, Status, MeetingType):
    return

def main():
    CheckInData = get_request_checkInData()
    person, CurrentTime, Status, MeetingType = JsonLoad(CheckInData)
    speakResult(person, CurrentTime, Status, MeetingType)

main()