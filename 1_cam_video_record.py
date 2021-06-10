import cv2

#Capture video from webcam
vid_capture = cv2.VideoCapture('/dev/video0')
vid_capture.set(1, 20.0) #Match fps
vid_capture.set(3,640)   #Match width
vid_capture.set(4,480)   #Match height

vid_cod = cv2.VideoWriter_fourcc(*'XVID')
output = cv2.VideoWriter("videos/cam_video0.mp4", vid_cod, 20.0, (640,480))

while(True):
     # Capture each frame of webcam video
     ret,frame = vid_capture.read()
     cv2.imshow("My cam video", frame)
     output.write(frame)
     # Close and break the loop after pressing "x" key
     if cv2.waitKey(1) &0XFF == ord('x'):
         break

# close the already opened camera
vid_capture.release()
# close the already opened file
output.release()
# close the window and de-allocate any associated memory usage
cv2.destroyAllWindows()