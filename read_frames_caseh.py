from util.caseh.video_capture_thread import VideoCaptureThread
from util.caseh.video_record_thread import VideoRecordThread
from util.fullface.frame_recon import FrameReconFullFace
from gpiozero import LED, Button
from queue import Queue
from imutils.video import FPS
import argparse
import imutils
import time, datetime, logging
import cv2

# Define LED de saída
# PIN11 = GPIO17
led_green = LED(17)
led_red = LED(27)
led_yellow = LED(22)


btn_main = Button(24)
btn_aux = Button(23)

def timestampFrame(fr):
	fr = imutils.resize(fr, width=640)
	dt = str(datetime.datetime.now())
	cv2.putText(fr, dt, (390, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

	return fr

def control_led(retry_num, max_retry, led_current_status):
	if int(retry_num) > 0 and int(retry_num) <= int(max_retry):
		if int(retry_num) >= int(float(max_retry) * 0.85):
			led_red.blink(0.25)
			# led_green.on()
		else:
			led_red.blink(0.75)
			# led_green.on()
			print("[RECON] PISCAR LED 0.75 - DateTime: " + dtn.strftime('%Y-%m-%d_%H_%M_%S'))
	else:
		# Se não estiver dentro das retentativas coloca o estado atual
		if frf.recon_status == True:
			led_red.off()
			led_green.on()
			if led_current_status != True:
				print("[RECON] LIGAR LED - DateTime: " + dtn.strftime('%Y-%m-%d_%H_%M_%S'))
				led_current_status = True
		else:
			led_red.on()
			led_green.off()
			if led_current_status != False:
				print("[RECON] DESLIGAR LED - DateTime: " + dtn.strftime('%Y-%m-%d_%H_%M_%S'))
				led_current_status = False
	return led_current_status

def check_buttons():
	if btn_main.is_pressed:
		print("[BUTTON] BTN_MAIN - DateTime: " + dtn.strftime('%Y-%m-%d_%H_%M_%S'))
	if btn_aux.is_pressed:
		print("[BUTTON] BTN_AUX - DateTime: " + dtn.strftime('%Y-%m-%d_%H_%M_%S'))


# Liga teste dos LEDs
led_green.on()
led_red.on()

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
ap.add_argument("-rr", "--recon_retry", required=False,
	help="Number of times to retry the recon")
ap.add_argument("-rp", "--recon_period", required=False,
	help="Time in seconds to trigger a recon and counter operation")

args = vars(ap.parse_args())

video_source = args["video"]
show_video = args["show"]
record_video = args["record"]
fps_to_video = args["fps"]
recon_faces = args["recon_faces"]
recon_retry = args["recon_retry"]
recon_period= args["recon_period"]
last_minute = -1

quit = False

print("[INFO] starting video thread from: " + video_source)

# variavel para guardar status corrente do LED:
led_current_status = False

queue = Queue(maxsize=256)
vct = VideoCaptureThread(args["video"], queue, transform=timestampFrame).start()
if recon_faces:
	frf = FrameReconFullFace('recon/todo/', 'recon/cropped/', 'recon/done/', max_retry=recon_retry)

fps = FPS().start()

vrt = None
if record_video == 'True':
	vrt = VideoRecordThread(video_source, queue).start()

# Desliga teste dos LEDs
led_green.off()
led_red.off()

# Reconhecimento ligado? Pisca 2x LED de controle (amarelo)

# loop over frames from the video file stream
while vct.running():
	frame = vct.read()
	# show the frame and update the FPS counter
	if show_video == 'True':
		if record_video == 'True':
			vrt.show_frame()
		else:
			cv2.imshow(video_source, frame)

	print("[RECON] Is active? bool(recon_faces): " + str(bool(recon_faces)) + " recon_faces: " + str(recon_faces))
	if bool(recon_faces):
		dtn = datetime.datetime.now()
		minute = int(dtn.strftime('%M'))
		second = int(dtn.strftime('%S'))
		diff_from_last_recon = int((dtn - frf.last_recon_datetime).total_seconds())

		# print("[RECON] Condiçoes 1 RECON: (diff_from_last_recon > int(recon_period) " + str(diff_from_last_recon > int(recon_period)))
		# print("[RECON] Condiçoes 2 RECON: (frf.recon_status == False and int(frf.recon_retry) >= int(recon_retry) " + str((frf.recon_status == False and int(frf.recon_retry) >= int(recon_retry))))
		if (diff_from_last_recon > int(recon_period)):
			if (frf.recon_status == False and int(frf.recon_retry) >= int(recon_retry)):
				frf.set_frame(frame, video_source)
				print("[RECON] Setting frame to RECON - DateTime: " + dtn.strftime('%Y-%m-%d_%H_%M_%S'))


		# verifica se o num de retentativas de identificação é maior 0
		# se for começa a piscar o led
		led_current_status = control_led(frf.recon_retry, recon_retry, led_current_status)

	# verifica botoes
	check_buttons()

	# Press Q on keyboard to stop recording
	key = cv2.waitKey(1)
	if key == ord('q') or quit == True:
		led_green.off()
		led_red.off()
		cv2.destroyAllWindows()
		break

	if vct.Q.qsize() < 2:  # If we are low on frames, give time to producer
		time.sleep(0.001)  # Ensures producer runs now, so 2 is sufficient
	fps.update()
	frame = None


# stop the timer and display FPS information
fps.stop()
print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

led_red.off()
led_green.off()

# do a bit of cleanup
cv2.destroyAllWindows()
vct.stop()
frf.stop()
# deliga LED
exit(1)