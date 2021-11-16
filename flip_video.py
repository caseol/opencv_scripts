# importing cv2
import cv2
import face_recognition

# path
path = 'videos_teste/rasp4b/monit_2021-11-13_17_55.avi'
cascade = 'resources/haarcascades/haarcascade_upperbody.xml'
detector = cv2.CascadeClassifier(cascade)

vs = cv2.VideoCapture(path)
ret, frame = vs.read()
(H, W) = frame.shape[:2]

fourcc = cv2.VideoWriter_fourcc(*"MJPG")
writer = cv2.VideoWriter('output/monit_2021-11-13_17_55_inv.avi', fourcc, 30, (W, H), True)

while True:
    # Reading an image in default mode
    ret, frame = vs.read()

    # Window name in which image is displayed
    window_name = 'INVERTIDO: 0'

    # Using cv2.flip() method
    # Use Flip code 0 to flip vertically
    image = cv2.flip(frame, -1)

    # check to see if we should write the frame to disk
    if writer is not None:
        writer.write(frame)

    # Displaying the image
    cv2.imshow(window_name, image)

    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


