# import required libraries
from time import sleep

from vidgear.gears import CamGear
import cv2
import datetime


def filterFrame(fr, fps):
    dt = str(datetime.datetime.now())
    cv2.putText(fr, "FPS: {}".format(str(fps)), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    cv2.putText(fr, dt, (390, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    return fr


# open any valid video stream(for e.g `myvideo.avi` file)
stream = CamGear(source="/dev/video0", logging=True, backend=0).start()

sleep(3)
# loop over
while True:

    # read frames from stream
    frame = stream.read()

    frame = filterFrame(frame, stream.framerate)

    # check for frame if Nonetype
    if frame is None:
        break

    # {do something with the frame here}

    # Show output window
    cv2.imshow("Output", frame)

    # check for 'q' key if pressed
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

# close output window
cv2.destroyAllWindows()

# safely close video stream
stream.stop()
