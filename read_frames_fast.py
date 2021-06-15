# Modified from:
# https://www.pyimagesearch.com/2017/02/06/faster-video-file-fps-with-cv2-videocapture-and-opencv/

# Performance:
#    Python 2.7: 105.78   --> 131.75
#    Python 3.7:  15.36   -->  50.13

# USAGE
# python read_frames_fast.py --video videos/jurassic_park_intro.mp4

# import the necessary packages
from util.imutis.file_video_stream import FileVideoStream
from util.save_video_output import SaveVideoOutput
from imutils.video import FPS
import numpy as np
import argparse
import imutils
import time, datetime
import cv2

def filterFrame(frame):
	frame = imutils.resize(frame, width=450)
	#frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

	# display the size of the queue on the frame
	dt = str(datetime.datetime.now())
	cv2.putText(frame, "Queue Size: {}".format(fvs.Q.qsize()), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 2)
	cv2.putText(frame, dt, (250, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 2)

	frame = np.dstack([frame, frame, frame])
	return frame

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", required=True,
	help="path to USB device")
ap.add_argument("-s", "--show", required=False,
	help="show video")
ap.add_argument("-r", "--record", required=True,
	help="save video output")
args = vars(ap.parse_args())

video_source = args["video"]
show_video = args["show"]
record_video = args["record"]
last_minute = -1
# start the file video stream thread and allow the buffer to
# start to fill
print("[INFO] starting video thread from: " + video_source)
# fvs = FileVideoStream(args["video"], transform=filterFrame).start()
fvs = FileVideoStream(args["video"], transform=filterFrame).start()
fps = FPS().start()

# Set up codec and output video settings
#codec = cv2.VideoWriter_fourcc('M','J','P','G')
#output_video = cv2.VideoWriter("videos/" + video_source.split('/')[-1] + "_init.avi", codec, 18, (640,480))

webcam_videowriter = SaveVideoOutput(fvs)

if record_video == 'True':
	webcam_videowriter.start()

# loop over frames from the video file stream
while fvs.running():
	# grab the frame from the threaded video file stream, resize
	# it, and convert it to grayscale (while still retaining 3
	# channels)
	# frame = fvs.read()

	if record_video == 'True' and show_video == 'True':
		webcam_videowriter.show_frame(True)

	# Press Q on keyboard to stop recording
	key = cv2.waitKey(1)
	if key == ord('q'):
		# salva
		cv2.destroyAllWindows()
		fps.stop()
		print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
		print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

		# do a bit of cleanup
		cv2.destroyAllWindows()
		fvs.stop()
		exit(1)

	if fvs.Q.qsize() < 2:  # If we are low on frames, give time to producer
		time.sleep(0.001)  # Ensures producer runs now, so 2 is sufficient
	fps.update()

# stop the timer and display FPS information
fps.stop()
if record_video == 'True':
	webcam_videowriter.stop()

print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

# do a bit of cleanup
cv2.destroyAllWindows()
fvs.stop()