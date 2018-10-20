import io
import socket
import picamera

server_socket = socket.socket()
server_socket.bind(('0.0.0.0', 8000))
server_socket.listen(0)
    
with picamera.PiCamera() as camera:
    camera.resolution = (640, 480)
    camera.start_preview()

    connection = server_socket.accept()[0].makefile('wb')
    print("Connecting")

    try:
        stream = io.BytesIO()
        camera.capture(stream, 'jpeg')
        stream.seek(0)
        connection.write(stream.read())
        stream.seek(0)
        stream.truncate()

    finally:
        connection.close()
        server_socket.close()
        camera.stop_preview()
        print("Connection closed")