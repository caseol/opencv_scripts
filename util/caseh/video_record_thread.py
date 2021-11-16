from util.caseh.video_upload_thread import VideoUploadThread
from threading import Thread
import _thread
import cv2
import time
import datetime
import subprocess
import logging


class VideoRecordThread(object):
    def __init__(self, source, queue, prefix_name, fps=30):

        # flag control
        self.stopped = False
        self.Q = queue
        self.fps = fps
        self.prefix_name = prefix_name

        # name of the source
        self.video_source = source

        self.dt = datetime.datetime.now()

        # Set up codec and output video settings
        self.codec = cv2.VideoWriter_fourcc('M','J','P','G')
        self.codec = cv2.VideoWriter_fourcc('D','I','V','X')
        # self.codec = cv2.VideoWriter_fourcc('T', 'H', 'E', 'O')
        # self.output_path = "videos/" + self.video_source.split('/')[-1] + "_" + self.dt.strftime('%Y-%m-%d_%H_%M')+".avi"
        self.output_path = "videos/" + self.prefix_name + self.dt.strftime('%Y-%m-%d_%H_%M')+".avi"
        self.output_video = cv2.VideoWriter(self.output_path, self.codec, self.fps, (640, 480))

        # inicializa variável do frame
        self.frame = 0
        self.invert_frame = False

        # Start the thread to read frames from the video stream
        self.thread = Thread(target=self.save_frame, args=())
        self.thread.daemon = True

    def start(self):
        # start a thread to read frames from the file video stream
        self.thread.start()
        return self

    def save_frame(self):
        # Read the next frame from the stream in a different thread
        last_minute = -1
        while True:
            # if the thread indicator variable is set, stop the
            # thread
            if self.stopped:
                break

            # otherwise, ensure the queue has room in it
            if not self.Q.full():
                self.frame = self.Q.get()
                if self.invert_frame:
                    self.frame = cv2.flip(self.frame, -1)
                dtn = datetime.datetime.now()
                minute = int(dtn.strftime('%M'))

                if (minute % 5 == 0) and (last_minute != minute):
                    last_minute = minute
                    self.output_video.release()
                    # self.output_path = "videos/" + self.video_source.split('/')[-1] + "_" + self.dt.strftime('%Y-%m-%d_%H_%M')+".avi"
                    self.output_path = "videos/" + self.prefix_name + dtn.strftime('%Y-%m-%d_%H_%M') + ".avi"
                    self.output_video = cv2.VideoWriter(self.output_path, self.codec, self.fps, (640, 480))
                    print("[INFO] " + self.output_path + " criado!")

                    vut = VideoUploadThread().start()

                self.output_video.write(self.frame)
            else:
                print("[INFO] fila cheia! dando tempo para o worker trabalhar..." + self.output_path)
                time.sleep(0.2)  # Rest for 10ms, we have a full queue

        print("[INFO] Fim da gravação" + self.output_path)

    def show_frame(self):
        # Display frames in main program
        cv2.imshow(self.video_source, self.frame)

        # Press Q on keyboard to stop recording
        key = cv2.waitKey(1)
        if key == ord('q'):
            self.output_video.release()
            cv2.destroyAllWindows()
            exit(1)

    def more(self):
        # return True if there are still frames in the queue. If stream is not stopped, try to wait a moment
        tries = 0
        while self.Q.qsize() == 0 and not self.stopped and tries < 10:
            time.sleep(0.2)
            tries += 1

        return self.Q.qsize() > 0
