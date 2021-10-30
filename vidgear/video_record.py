# import required libraries
from vidgear.gears import CamGear
import cv2


# define suitable tweak parameters for your stream.
options = {
    "CAP_PROP_FRAME_WIDTH": 320,
    "CAP_PROP_FRAME_HEIGHT": 240,
    "CAP_PROP_FPS": 30,
}

# To open live video stream on webcam at first index(i.e. 0)
# device and apply source tweak parameters
stream = CamGear(source=0, logging=True, **options).start()

# loop over
while True:

    # read frames from stream
    frame = stream.read()

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