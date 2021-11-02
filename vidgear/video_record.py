# import required libraries
from vidgear.gears import WriteGear
import cv2
import datetime


def timestampFrame(fr):
	# fr = imutils.resize(fr, width=640)
	dt = str(datetime.datetime.now())
	cv2.putText(fr, dt, (390, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

	return fr
# define suitable (Codec,CRF,preset) FFmpeg parameters for writer
output_params = {"-vcodec": "libx264", "-crf": 0, "-preset": "fast"}
#output_params = {"-vcodec": "MP4V", "-crf": 0, "-preset": "fast", "-fps": 30}

# Open suitable video stream, such as webcam on first index(i.e. 0)
stream = cv2.VideoCapture(0)

# Define writer with defined parameters and suitable output filename for e.g. `Output.mp4`
writer = WriteGear(output_filename = 'Output.avi', logging = True, **output_params)

# loop over
while True:

    # read frames from stream
    (grabbed, frame) = stream.read()

    # check for frame if not grabbed
    if not grabbed:
      break

    # {do something with the frame here}
    # lets convert frame to gray for this example
    # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # write gray frame to writer
    frame = timestampFrame(frame)
    writer.write(frame)

    # Show output window
    cv2.imshow("Output Gray Frame", frame)

    # check for 'q' key if pressed
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

# close output window
cv2.destroysAllWindows()

# safely close video stream
stream.release()

# safely close writer
writer.close()
