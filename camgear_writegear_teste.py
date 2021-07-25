# import required libraries
from vidgear.gears import CamGear
from vidgear.gears import WriteGear
import cv2
import datetime
import face_recognition


def filterFrame(fr, fps):
    dt = str(datetime.datetime.now())
    cv2.putText(fr, "FPS: {}".format(str(fps)), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    cv2.putText(fr, dt, (390, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    return fr

faceCascade = cv2.CascadeClassifier("resources/haarcascades/haarcascade_frontalface_default.xml")
caseh_image = face_recognition.load_image_file("resources/caseh.jpg")
caseh_face_encoding = face_recognition.face_encodings(caseh_image)[0]

known_face_encodings = [
    caseh_face_encoding
]

known_face_names = [
    "Caseh"
]

# Initialize some variables
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True

# Open suitable video stream, such as webcam on first index(i.e. 0)
#stream = CamGear(source='/dev/video0').start()
stream = CamGear(source='resources/teste_camera_noturna.mp4').start()

# Define WriteGear Object with suitable output filename for e.g. `Output.mp4`
output_params = {"-fourcc": "MJPG", "-fps":  stream.framerate}
writer = WriteGear(output_filename = 'videos/teste_camera_noturna_mod.mp4', logging=True)


def face_bound(fr):
    imgGray = cv2.cvtColor(fr, cv2.COLOR_RGB2GRAY)
    faces = faceCascade.detectMultiScale(imgGray, 1.09, 3)
    for (x, y, w, h) in faces:
        cv2.rectangle(fr, (x, y), (x + w, y + h), (255, 0, 0), 1, 4)
    return fr

# loop over
while True:

    # read frames from stream
    frame = stream.read()

    # check for frame if None-type
    if frame is None:
        break

    # {do something with the frame here}
    frame = filterFrame(frame, stream.framerate)
    frame = face_bound(frame)

    # write frame to writer
    writer.write(frame)

    # Show output window
    cv2.imshow("Output Frame", frame)

    # check for 'q' key if pressed
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

# close output window
cv2.destroyAllWindows()

# safely close video stream
stream.stop()

# safely close writer
writer.close()