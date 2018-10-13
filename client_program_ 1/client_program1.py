#The server on Raspberry Pi send jpg image from Camera Module to client.
#It is always listening to incoming connection from clientself.
#To get image, just access and refresh the address to get instant image captured
#by the Raspberry Pi Camera Module.
#The image can be accessed on browsers at http://<Raspberry Pi IP>:8000

import io
import socket
import picamera
import atexit

def camServer():

    while True:
        print("waiting for connection")
        conn, addr = server_socket.accept()
        if conn:
            print(conn)
            print(addr)
            connection = conn.makefile('wb')
            break

    print("Connecting...")
    try:
        stream = io.BytesIO()
        camera.capture(stream, 'jpeg')
        stream.seek(0)
        connection.write(stream.read())
        stream.seek(0)
        stream.truncate()
    finally:
        print("Close connection.")
        connection.close()

def onExit():
    connection.close()
    server_socket.close()
    print("Exit.")

with picamera.PiCamera() as camera:
    camera.resolution = (640, 480)
    camera.start_preview()
    atexit.register(onExit)

    server_socket = socket.socket()
    server_socket.bind(('0.0.0.0', 8000))
    server_socket.listen(0)
    server_socket.setblocking(1)

    while True:
        camServer()