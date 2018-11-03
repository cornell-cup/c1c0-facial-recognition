#This Client Program 2 (Always Listening) receive JSON from Buffer program and record sign-in status.
#It also speak out with the result.
import json


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
