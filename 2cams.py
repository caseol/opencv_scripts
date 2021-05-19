import cv2
from face_detection import *

cap = cv2.VideoCapture('/dev/video0')
cap2 = cv2.VideoCapture('/dev/video2')

while True:

    ret, frame = cap.read()
    print(ret)

    ret2, frame2 = cap2.read()
    print(ret2)

    cv2.imshow('CAM 1', face_detection_from_frame(frame))
    cv2.imshow('CAM 2', frame2)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cap2.release()

cv2.destroyAllWindows()