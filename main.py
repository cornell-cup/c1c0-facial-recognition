import socket, time, threading

from client.camera import *
from client.client import *
from client.config import *
from client.rotation import *

# Computer architecture related settings.
IP: str = '127.0.0.1'
PORT: int = 1233
SLEEP_TIME: float = 0.5
DISPLAY: bool = True

def accept_data() -> None:
	"""
	Function for receiving and sending data to a socket.
	"""

	sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.bind((IP, PORT))
	sock.listen()

	while True:
		try:
			time.sleep(SLEEP_TIME)
			data = sock.recv(1024)

			if data:
				print(f'Received: {data}')
				sock.send(data)

		except OSError: pass

if __name__ == '__main__':
	client: Client = Client(ip=IP, load=False, port=PORT, cache_location=DEFAULT_CACHE_LOCATION, dev=None)
	# t0: threading.Thread = threading.Thread(target=accept_data, daemon=True); t0.start()
	# sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	try:
        # sock.connect((IP, PORT))
        # Later chatbot integration:
        # data = socket.recv(1024).decode()
        # client.interpret_task(data)

        # For now, just always take attendance.
		matches = client.take_attendance(disp=DISPLAY)

		matches = {match for matches_ in matches for match, _ in matches_}
		data = ", ".join(matches)
		print(f'Data: {data}')

		# sock.sendall(data.encode())
		# sock.close()
	finally: pass

	print('Test presumable passed.' if data else 'Test presumably failed.')
