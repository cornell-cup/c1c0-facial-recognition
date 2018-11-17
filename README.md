# r2-facial_recognition client program

###General Info

Language: Python

Trigger: keyborad

Result: robot's appropriate response

Must be manually triggered

###Description
This program must be manually triggered by keyboeard. It first gets images from Raspberry Pi and sends it to computing server by using POST request in HTTP protocol. The return value for the request (from the server) is a JSON value which contains information about the people's sign-in status, type of the meeting, and people's name and etc. Then make robots to response according to the JSON received.
