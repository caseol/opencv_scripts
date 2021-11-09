from util.caseh.video_capture_thread import VideoCaptureThread
from util.caseh.video_record_thread import VideoRecordThread
from util.caseh.frame_recon_thread import FrameReconThread
# from util.fullface.frame_recon import FrameReconFullFace

from gpiozero import LED, Button
from queue import Queue
from imutils.video import FPS
import argparse

import time
import datetime
# import logging
import cv2

# Define LED de saída
led_green = LED(17)
led_red = LED(27)
led_yellow = LED(22)


btn_main = Button(24)
btn_aux = Button(23)

def timestampFrame(fr):
	# fr = imutils.resize(fr, width=640)
	dt = str(datetime.datetime.now())
	cv2.putText(fr, dt, (390, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

	return fr

def control_led(retry_num, max_retry, led_current_status):
	if int(retry_num) > 0 and int(retry_num) <= int(max_retry):
		if int(retry_num) >= int(float(max_retry) * 0.85):
			print("[RECON] GREEN ON + PISCAR RED 0.25 - DateTime: " + dtn.strftime('%Y-%m-%d_%H_%M_%S'))
			led_red.blink(0.25)
			led_green.on()
		else:
			led_red.blink(0.75)
			led_green.on()
			print("[RECON] GREEN ON + PISCAR RED 0.75 - DateTime: " + dtn.strftime('%Y-%m-%d_%H_%M_%S'))
	else:
		# Se não estiver dentro das retentativas coloca o estado atual
		if frt.recon_status == True:
			led_red.off()
			led_green.on()
			if led_current_status != True:
				print("[RECON] RECON TRUE = LIGAR GREEN + RED OFF - DateTime: " + dtn.strftime('%Y-%m-%d_%H_%M_%S'))
				led_current_status = True
		else:
			led_red.on()
			led_green.off()
			if led_current_status != False:
				print("[RECON] RECON FALSE = GREEN OFF + RED ON - DateTime: " + dtn.strftime('%Y-%m-%d_%H_%M_%S'))
				led_current_status = False
	return led_current_status

# def check_buttons():
# 	if btn_main.is_pressed():
#  		print("[BUTTON] BTN_MAIN - DateTime: " + dtn.strftime('%Y-%m-%d_%H_%M_%S'))
#  	if btn_aux.is_pressed():
#  		print("[BUTTON] BTN_AUX - DateTime: " + dtn.strftime('%Y-%m-%d_%H_%M_%S'))
#

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
show_video = int(args["show"])
record_video = int(args["record"])
fps_to_video = args["fps"] or 30
recon_faces = int(args["recon_faces"])
recon_retry = int(args["recon_retry"]) or 3
recon_period = int(args["recon_period"]) or 10
last_minute = -1

quit = False

print("[INFO] starting video thread from: " + video_source)

# variavel para guardar status corrente do LED:
led_current_status = False

fps = FPS().start()

queue = Queue(maxsize=256)
vct = VideoCaptureThread(args["video"], queue, transform=timestampFrame).start()

prefix_name = ""
if bool(recon_faces):
	frt = FrameReconThread('recon/todo/', 'recon/cropped/', 'recon/done/', max_retry=recon_retry)
	prefix_name = "recon_"
else:
	prefix_name = "monit_"

vrt = None
if bool(record_video):
	vrt = VideoRecordThread(video_source, queue, prefix_name).start()

# Desliga teste dos LEDs
led_green.off()
led_red.off()

# Reconhecimento ligado? Pisca 2x LED de controle (amarelo)

# loop over frames from the video file stream
while vct.running():
	dtn = datetime.datetime.now()
	frame = vct.read()

	if bool(recon_faces):
		if frt.stopped:
			frt.start()
			print("[RECON] Inicia worker de reconhecimento: frt.start()")
			time.sleep(3)

		minute = int(dtn.strftime('%M'))
		second = int(dtn.strftime('%S'))
		diff_from_last_recon = int((dtn - frt.last_recon_datetime).total_seconds())

		# dispara o reconhecimento a cada recon_period
		if second % int(recon_period) == 0:
			if frt.queue.not_full:
				frt.set_frame(frame)
				print("[RECON] set_frame segundo: " + str(second))

		# verifica se o num de retentativas de identificação é maior 0
		# se for começa a piscar o led
		dtn_final = datetime.datetime.now() - dtn
		print("[RECON] RECON STATUS:" + str(frt.recon_status) + " - RETRY:" + str(frt.recon_retry) + " - " + str(diff_from_last_recon) + " - " + dtn.strftime('%Y-%m-%d_%H_%M_%S'))

		# Controla LEDs
		led_current_status = control_led(frt.recon_retry, recon_retry, led_current_status)
	else:
		print("[RECON] DESLIGADO!")

	# verifica botoes
	# check_buttons()

	if show_video == 'True':
		cv2.imshow(video_source, frame)
	else:
		print("[RECON] NÃO MOSTRA VÍDEO " + dtn.strftime('%Y-%m-%d_%H_%M_%S'))


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

# led_red.off()
# led_green.off()

# do a bit of cleanup
cv2.destroyAllWindows()
vct.stop()
if not frt.stopped:
	frt.stop()

# deliga LED
exit(1)
