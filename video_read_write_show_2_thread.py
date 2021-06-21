import cv2
from util.caseh.video_capture_thread import VideoCaptureThreading

cap = VideoCaptureThreading('/dev/video0')
cap2 = VideoCaptureThreading('/dev/video2')
cap.start()
cap2.start()
while True:
    ret, frame = cap.read()
    ret2, frame2 = cap2.read()

    cv2.imshow('/dev/video0',frame)
    cv2.imshow('/dev/video2',frame2)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        cap.stop()
        cap2.stop()
        break

cap.stop()
cap2.stop()
cap.release()
cap2.release()
cv2.destroyAllWindows()