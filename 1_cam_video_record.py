import cv2
import datetime
import os
from pathlib import Path

def get_file_size(file):
     size = Path(file).stat().st_size
     return size

def convert_bytes(size, unit=None):
     if unit == "KB":
          return round(size / 1024, 3)
     elif unit == "MB":
          return round(size / (1024 * 1024), 3)
     elif unit == "GB":
          return round(size / (1024 * 1024 * 1024), 3)
     else:
          return size

#Capture video from webcam
vid_capture = cv2.VideoCapture('video0')

vid_capture.set(1, 20.0) #Match fps
vid_capture.set(3,640)   #Match width
vid_capture.set(4,480)   #Match height

# vid_cod = cv2.VideoWriter_fourcc(*'XVID')
vid_cod = cv2.VideoWriter_fourcc(*'MP4V')


output = cv2.VideoWriter("videos/cam_video0.mp4", 0x7634706d, 20.0, (640,480))

while(True):
     # verifica se o tamanho do arquivo e para ou não a gravação
     video_size = convert_bytes(get_file_size("videos/cam_video0.mp4"), "MB")
     if video_size > 50:
          break
     # Capture each frame of webcam video
     ret,frame = vid_capture.read()
     if ret:
          font = cv2.FONT_HERSHEY_SIMPLEX
          dt = str(datetime.datetime.now())
          frame = cv2.putText(frame, dt, (120, 20), font, 0.7, (0, 0, 0), 2, cv2.INTER_LINEAR_EXACT)

     output.write(frame)
     #cv2.imshow("My cam video", frame)

     # Close and break the loop after pressing "x" key
     if cv2.waitKey(1) &0XFF == ord('x'):
         break


# close the already opened camera
vid_capture.release()
# close the already opened file
output.release()
# close the window and de-allocate any associated memory usage
cv2.destroyAllWindows()