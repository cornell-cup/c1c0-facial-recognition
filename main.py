import time, os

from client.camera import *
from client.client import *
from client.config import *
from client.rotation import *

# Global variables
SLEEP_TIME: float = 1

if __name__ == '__main__':
	client: Client = Client(load=False)

	while True:
		os.system('cls' if os.name == 'nt' else 'clear')
		inputs = input().split(' ')
		command, args = inputs[0].lower(), inputs[1:]

		if (command == 'exit' or command == 'e'): break
		if (command == 'quit' or command == 'q'): break
		task = client.interpret_task(command); task(args)
		time.sleep(SLEEP_TIME)
