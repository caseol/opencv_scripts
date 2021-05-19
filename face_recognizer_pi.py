# This is a demo of running face recognition on a Raspberry Pi.
# This program will print out the names of anyone it recognizes to the console.

# To run this, you need a Raspberry Pi 2 (or greater) with face_recognition and
# the picamera[array] module installed.
# You can follow this installation instructions to get your RPi set up:
# https://gist.github.com/ageitgey/1ac8dbe8572f3f533df6269dab35df65
import cv2
import face_recognition
import numpy as np

# Get a reference to the Raspberry Pi camera.
# If this fails, make sure you have a camera connected to the RPi and that you
# enabled your camera in raspi-config and rebooted first.
video_capture = cv2.VideoCapture('/dev/video2')
video_capture.set(3, 320)
video_capture.set(4, 240)
output = np.empty((240, 320, 3), dtype=np.uint8)

# Load a sample picture and learn how to recognize it.
print("carregando imagens autorizadas...")
obama_image = face_recognition.load_image_file("resources/obama.jpg")
obama_face_encoding = face_recognition.face_encodings(obama_image)[0]

biden_image = face_recognition.load_image_file("resources/biden.jpg")
biden_face_encoding = face_recognition.face_encodings(biden_image)[0]

caseh_image = face_recognition.load_image_file("resources/caseh.jpg")
caseh_face_encoding = face_recognition.face_encodings(caseh_image)[0]

known_face_encodings = [
    caseh_face_encoding,
    obama_face_encoding,
    biden_face_encoding
]
known_face_names = [
    "Carlos Andre",
    "Barack Obama",
    "Joe Biden"
]


# Initialize some variables
face_locations = []
face_encodings = []

while True:
    print("Capturing image.")
    # Grab a single frame of video from the RPi camera as a numpy array
    ret, frame = video_capture.read()

    # Find all the faces and face encodings in the current frame of video
    face_locations = face_recognition.face_locations(frame)
    print("Encontramos {} faces.".format(len(face_locations)))
    face_encodings = face_recognition.face_encodings(frame, face_locations)

    # Loop over each face found in the frame to see if it's someone we know.
    for face_encoding in face_encodings:
        # See if the face is a match for the known face(s)

        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Desconhecido"

        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            name = known_face_names[best_match_index]
            print("Encontramos {} faces na imagem.".format(len(face_locations)))
            print("Encontrado: {}!".format(name))
