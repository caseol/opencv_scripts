# import required libraries
from vidgear.gears import CamGear
from vidgear.gears import WriteGear
import cv2

# Open suitable video stream, such as webcam on first index(i.e. 0)
stream = CamGear(source='/dev/video4').start()

# Define WriteGear Object with suitable output filename for e.g. `Output.mp4`
writer = WriteGear(output_filename = 'videos/Output4.mp4')

# loop over
while True:

    # read frames from stream
    frame = stream.read()

    # check for frame if None-type
    if frame is None:
        break


    # {do something with the frame here}


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