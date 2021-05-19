import cv2

cap = cv2.VideoCapture('/dev/video0')

while True:

    ret, frame = cap.read()

    cv2.imshow('CAM 1',frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()

cv2.destroyAllWindows()