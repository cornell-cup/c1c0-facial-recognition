import dlib
import Image
from skimage import io,data
import matplotlib.pyplot as plt


def detect_faces(image):

    # Create a face detector
    face_detector = dlib.get_frontal_face_detector()

    # Run detector and get bounding boxes of the faces on image.
    detected_faces = face_detector(image, 1)
    face_frames = [(x.left()-200, x.top()-400,
                    x.right()+100, x.bottom()+100) for x in detected_faces]

    return face_frames

# Load image
img_path = './multiple_people.jpeg'

image = io.imread(img_path)

# Detect faces
detected_faces = detect_faces(image)
if(detected_faces):
    print("Face detected. Crop face processing...")
else:
    print("No face detected.")

# Crop faces and plot
for n, face_rect in enumerate(detected_faces):
    face = Image.fromarray(image).crop(face_rect)
    plt.subplot(1, len(detected_faces), n+1)
    plt.axis('off')
    plt.imshow(face)
    plt.show()
