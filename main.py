import socket, time, threading, os

from client.camera import *
from client.client import *
from client.config import *
from client.rotation import *

# Computer architecture related settings.
IP: str           = '127.0.0.1'
PORT: int         = 1233
SLEEP_TIME: float = 0.5
DISPLAY: bool     = True
# DEV: str          = 'v4l2src device=/dev/video0 ! videoconvert ! appsink'

if __name__ == '__main__':
	client: Client = Client(ip=IP, load=False, port=PORT, cache_location=DEFAULT_CACHE_LOCATION)

	while True:
		os.system('cls' if os.name == 'nt' else 'clear')
		command = input().lower()

		if (command == 'exit' or command == 'quit'): break
		task = client.interpret_task(command); task()
		time.sleep(1)
