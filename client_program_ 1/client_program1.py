#The server on Raspberry Pi send jpg image from Camera Module to client.
#It is always listening to incoming connection from client, and is manually triggered by
#accessing the address to get instant image captured by the Raspberry Pi Camera Module.
#The image can be accessed on browsers at http://169.254.155.200:8000

import io
import socket
import picamera
import atexit

# def test():
#     server_socket = socket.socket()
#     server_socket.bind(('127.0.0.1', 8000))
#     server_socket.listen(0)
#     server_socket.setblocking(1)
#     print("start working")
#     conn, addr = server_socket.accept()
#     if conn:
#         print(conn)
#         print(addr)
#         connection = conn.makefile('wb')
#     print("Connecting...")
#
#     try:
#         f = open('testImage.png', 'r+')
#         jpgdata = f.read()
#         f.close()
#         connection.write(jpgdata)
#     finally:
#         print("Close connection.")
#         connection.close()

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
    server_socket.bind(('169.254.155.200', 8000))
    server_socket.listen(0)
    server_socket.setblocking(1)

while True:
    camServer()
    # test()
