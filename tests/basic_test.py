import socket
import time
import threading

from r2_facial_recognition.client import Client

CACHE_LOCATION = '.cache'
PATH = 'resources/people'

# TODO: Disambiguate socket IP and remote server IP.
IP = '127.0.0.1'
PORT = 1233
SLEEP_TIME = 0.5
DEVICE = -1

LOCAL = True
DISPLAY = True

def accept_data():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((IP, PORT))
    sock.listen()
    while True:
        try:
            time.sleep(SLEEP_TIME)
            data = sock.recv(1024)
            if data:
                print(f'Received: {data}')
                sock.send(data)
        except OSError:
            print('No data yet.')


if __name__ == '__main__':
    client = Client(path=PATH, ip=IP, port=PORT, cache_location=CACHE_LOCATION, dev=None)

    t0 = threading.Thread(target=accept_data, daemon=True)

    t0.start()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((IP, PORT))
        # Later chatbot integration:
        # data = socket.recv(1024).decode()
        # client.interpret_task(data)
        
        # For now, just always take attendance.
        print('Taking attendance')
        matches = client.take_attendance(disp=DISPLAY)
        data = ",".join(matches)
        print(f'Sending: {data}')
        sock.sendall(data.encode())
    finally:
        sock.close()
