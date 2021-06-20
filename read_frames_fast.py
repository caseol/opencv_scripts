# Modified from:
# https://www.pyimagesearch.com/2017/02/06/faster-video-file-fps-with-cv2-videocapture-and-opencv/

# Performance:
#    Python 2.7: 105.78   --> 131.75
#    Python 3.7:  15.36   -->  50.13

# USAGE
# python read_frames_fast.py --video videos/jurassic_park_intro.mp4

# import the necessary packages
from util.imutils.filevideostream import FileVideoStream
from util.imutils.save_video_output import SaveVideoOutput
from queue import Queue
from imutils.video import FPS
import numpy as np
import argparse
import imutils
import time, datetime
import cv2

def filterFrame(fr):
	# display the size of the queue on the frame
	fr = imutils.resize(fr, width=640)
	fr = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY)

	f = np.dstack([fr, fr, fr])

	dt = str(datetime.datetime.now())
	cv2.putText(fr, "Queue Size: {}".format(fvs.Q.qsize()), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
	cv2.putText(fr, dt, (390, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

	return fr

def timestampFrame(fr):
	frame = imutils.resize(fr, width=640)
	dt = str(datetime.datetime.now())
	cv2.putText(fr, dt, (390, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

	return fr

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", required=True,
	help="path to USB device")
ap.add_argument("-s", "--show", required=False,
	help="show video")
ap.add_argument("-r", "--record", required=True,
	help="save video output")
ap.add_argument("-f", "--fps", required=True,
	help="path to USB device")
args = vars(ap.parse_args())

video_source = args["video"]
show_video = args["show"]
record_video = args["record"]
fps_to_video = args["fps"]
last_minute = -1
# start the file video stream thread and allow the buffer to
# start to fill
print("[INFO] starting video thread from: " + video_source)
# fvs = FileVideoStream(args["video"], transform=filterFrame).start()

queue = Queue(maxsize=256)
fvs = FileVideoStream(args["video"], queue, transform=filterFrame).start()
fps = FPS().start()

svo = None
if record_video == 'True':
	svo = SaveVideoOutput(video_source, queue).start()

# loop over frames from the video file stream
while fvs.running():
	# grab the frame from the threaded video file stream, resize
	# it, and convert it to grayscale (while still retaining 3
	# channels)
	frame = fvs.read()
	# show the frame and update the FPS counter
	if show_video == 'True':
		cv2.imshow(video_source, frame)

	# Press Q on keyboard to stop recording
	key = cv2.waitKey(1)
	if key == ord('q'):
		cv2.destroyAllWindows()
		break

	if fvs.Q.qsize() < 2:  # If we are low on frames, give time to producer
		time.sleep(0.001)  # Ensures producer runs now, so 2 is sufficient
	fps.update()

# stop the timer and display FPS information
fps.stop()
print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

# do a bit of cleanup
cv2.destroyAllWindows()
fvs.stop()
exit(1)