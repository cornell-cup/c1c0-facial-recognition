import face_recognition
from PIL import Image

# find largest face in the image
# return None if no face is found or the face is too small
# (less than 1/12 of the image)
def find_face(image):
    face_locations = face_recognition.face_locations(image)
    for face_location in face_locations:
        top, right, bottom, left = face_location
        image_x, image_y, d = image.shape
        # minimal threshold to reject a face result
        threshold = min(image_x, image_y) / 12
        if right - left > threshold:
            # a qualifying face
            return face_location
    return None

def main():
# capture image
    image_unavailable = False
    while (image_unavailable == False):
        with picamera.PiCamera() as camera:
            image = camera.capture("test.png")
        face_location = find_face(image)
        if face_location != None:
            top, right, bottom, left = face_location
            # check if the face is within the middle 20% of the image
            face_center = (right + left) / 2
            image_x, image_y, d = image.shape
            if face_center > image_x * 0.4 and face_center < image_x * 0.6:
                # crop image
                face_image = image[top:bottom, left:right]
                pil_image = Image.fromarray(face_image)
                pil_image.save('/alittletest.png', 'PNG')
                break
        # rotate head
        print("rotate head")

main()