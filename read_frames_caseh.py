from util.caseh.video_capture_thread import VideoCaptureThread
from util.caseh.video_record_thread import VideoRecordThread
from util.fullface.frame_recon import FrameReconFullFace
from queue import Queue
from imutils.video import FPS
import argparse
import imutils
import time, datetime, sys
import cv2
import RPi.GPIO as GPIO

# Define LED de saída
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
# PIN11 = GPIO17
GPIO.setup(11, GPIO.OUT)


def timestampFrame(fr):
	fr = imutils.resize(fr, width=640)
	dt = str(datetime.datetime.now())
	cv2.putText(fr, dt, (390, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

	return fr

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", required=True,
	help="define video path")
ap.add_argument("-s", "--show", required=False,
	help="show video window")
ap.add_argument("-r", "--record", required=True,
	help="save video output")
ap.add_argument("-f", "--fps", required=True,
	help="define FPS")
ap.add_argument("-rf", "--recon_faces", required=False,
	help="active face recognition")
args = vars(ap.parse_args())

video_source = args["video"]
show_video = args["show"]
record_video = args["record"]
fps_to_video = args["fps"]
recon = args["recon_faces"]
last_minute = -1

quit = False
# start the file video stream thread and allow the buffer to
# start to fill
print("[INFO] starting video thread from: " + video_source)
# fvs = FileVideoStream(args["video"], transform=filterFrame).start()

queue = Queue(maxsize=256)
vct = VideoCaptureThread(args["video"], queue, transform=timestampFrame).start()
frf = FrameReconFullFace('recon/todo/', 'recon/cropped/', 'recon/done/').start()
fps = FPS().start()

vrt = None
if record_video == 'True':
	vrt = VideoRecordThread(video_source, queue).start()

# loop over frames from the video file stream
while vct.running():
	# Define LED de saída
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BOARD)
	# PIN11 = GPIO17
	GPIO.setup(11, GPIO.OUT)

	frame = vct.read()
	# show the frame and update the FPS counter
	if show_video == 'True':
		#cv2.imshow(video_source, frame)
		vrt.show_frame()

	if True:
		dtn = datetime.datetime.now()
		minute = int(dtn.strftime('%M'))
		second = int(dtn.strftime('%S'))
		if (second % 10 == 0):
			frf.set_frame(frame, video_source)
			print("[RECON] Starting RECON - DateTime: " + dtn.strftime('%Y-%m-%d_%H_%M_%S'))
	if frf.recon_status == True:
		GPIO.output(12, GPIO.HIGH)
		print("[RECON] LIGA LED - DateTime: " + dtn.strftime('%Y-%m-%d_%H_%M_%S'))
	else:
		GPIO.output(12, GPIO.LOW)
		print("[RECON] DESLIGA LED - DateTime: " + dtn.strftime('%Y-%m-%d_%H_%M_%S'))

	# Press Q on keyboard to stop recording
	key = cv2.waitKey(1)
	if key == ord('q') or quit == True:
		cv2.destroyAllWindows()
		break

	if vct.Q.qsize() < 2:  # If we are low on frames, give time to producer
		time.sleep(0.001)  # Ensures producer runs now, so 2 is sufficient
	fps.update()

# stop the timer and display FPS information
fps.stop()
print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

# do a bit of cleanup
cv2.destroyAllWindows()
vct.stop()
frf.stop()
exit(1)