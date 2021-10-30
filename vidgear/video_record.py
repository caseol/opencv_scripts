# import required libraries
from vidgear.gears import CamGear
from vidgear.gears import WriteGear
import cv2

# open any valid video stream(for e.g `myvideo.avi` file)
options = {
    "CAP_PROP_FRAME_WIDTH": 640,
    "CAP_PROP_FRAME_HEIGHT": 480,
    "CAP_PROP_FPS": 30,
}

stream = CamGear(source=0, logging=True, **options).start()

# Define writer with Non-compression mode and suitable output filename for e.g. `Output.mp4`
writer = WriteGear(output_filename="Output.mp4", compression_mode=False)

# loop over
while True:

    # read frames from stream
    frame = stream.read()

    # check for frame if Nonetype
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