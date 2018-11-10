# import io
# import socket
# import picamera

# server_socket = socket.socket()
# server_socket.bind(('0.0.0.0', 8000))
# server_socket.listen(0)
    
# with picamera.PiCamera() as camera:
#     camera.resolution = (640, 480)
#     camera.start_preview()

#     connection = server_socket.accept()[0].makefile('wb')
#     print("Connecting")

#     try:
#         stream = io.BytesIO()
#         camera.capture(stream, 'jpeg')
#         stream.seek(0)
#         connection.write(stream.read())
#         stream.seek(0)
#         stream.truncate()

#     finally:
#         connection.close()
#         server_socket.close()
#         camera.stop_preview()
#         print("Connection closed")

import io
import socket
import picamera
import atexit
import keyboard

def camServer():

    while True:
        print("wait...")
        conn, addr = server_socket.accept()
        if conn:
            print(conn)
            print(addr)
            connection = conn.makefile('wb')
            break

    print("Connecting")
    try:
        stream = io.BytesIO()
        camera.capture(stream, 'jpeg')
        stream.seek(0)
        connection.write(stream.read())
        stream.seek(0)
        stream.truncate()
    finally:
        print("close connection")
        connection.close()

def onExit():
    connection.close()
    server_socket.close()
    print("exit")

with picamera.PiCamera() as camera:
    camera.resolution = (640, 480)
    camera.start_preview()
    atexit.register(onExit)

    server_socket = socket.socket()
    server_socket.bind(('0.0.0.0', 8000))
    server_socket.listen(0)
    server_socket.setblocking(1)

    #we listen to the keyboard event pressing a
    while True:
        if keyboard.is_pressed('a'):
            camServer()
        else:
            pass
