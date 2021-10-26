from threading import Thread
import cv2, time, datetime
import face_recognition
import numpy as np


class FrameReconThread(object):
    def __init__(self, path_todo='recon/todo/', path_cropped='recon/cropped/', path_not_cropped='recon/not_cropped/',
                 path_done='recon/done/', max_retry=3):
        # flag control
        self.stopped = False
        self.dt = datetime.datetime.now()

        # inicializa variável do frame
        self.frame = 0
        self.small_frame = 0

        # incitialize paths
        self.path_todo = path_todo
        self.path_cropped = path_cropped
        self.path_not_cropped = path_not_cropped
        self.path_done = path_done

        self.recon_status = False
        self.last_recon_datetime = (datetime.datetime.now() - datetime.timedelta(hours=3))
        self.recon_retry = 0
        self.max_retry = int(max_retry)
        self.do_cropper = False

        # Start the thread to read frames from the video stream
        self.thread = Thread(target=self.recon_frame, args=())
        self.thread.daemon = True

    def start(self):
        # start a thread to read frames from the file video stream
        self.thread.start()
        return self

    def set_frame(self, frame):
        self.frame = frame
        # Resize frame of video to 1/4 size for faster face recognition processing
        self.small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

    def recon_frame(self):
        # Read the next frame from the stream in a different thread
        last_minute = -1
        while self.frame != 0:
            # if the thread indicator variable is set, stop the thread
            if self.stopped:
                break

            dtn = datetime.datetime.now()
            minute = int(dtn.strftime('%M'))

            # FAZ O RECON AQUI

        print("[INFO] Fim do RECON" + self.output_path)

