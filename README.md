# r2-facial_recognition client program

### General Info

Language: Python

Trigger: keyborad

Result: robot's appropriate response

Must be manually triggered

### Description
This program must be manually triggered by keyboard. It first gets images from Raspberry Pi and sends it to computing server by using POST request in HTTP protocol. The return value for the request (from the server) is a JSON value which contains information about the people's sign-in status, type of the meeting, and people's name and etc. Then make robots to response according to the JSON received. The R2 robot is actually saying out the name of the perosn and "successfuly checked in."" This is for pi to speak out to give people direct response on whether they are succeesfully signed in. The volume, speed, and voice of the speaker can be modified in this program and it can also count down numbers in case it's necessary.

### Archived Branches

- `intel_demo`: A branch used right before a specific demo, lost its purpose afterwards, and became stale, so it was archived.

To see the above archived branches, checkout the tags of this repository.
