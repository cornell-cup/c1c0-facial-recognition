# r2-facial_recognition client program

###General Info

Language: Python

Trigger: keyborad

Result: robot's appropriate response

Must be manually triggered

###Description
This program must be manually triggered by keyboeard. It first gets images from Raspberry Pi and sends it to computing server by using POST request in HTTP protocol. The return value for the request (from the server) is a JSON value which contains information about the people's sign-in status, type of the meeting, and people's name and etc. Then make robots to response according to the JSON received.

#saying-words

###General information

Language: Python

Input: text

Output: Pi speaking out according to the text

###	Description
This is for pi to speak out to give people direct response on whether they are succeesfully signed in.
The returned information includes "name + you are successfuly signed in!"
The volume, speed, and voice of the speaker can be modified in this program and it can also count down numbers in case it's necessary.