from queue import Queue
from threading import Thread, Lock
import cv2, time, datetime, imutils

class VideoRecordThreading:
    def __init__(self, src=0, width=640, height=480):
        self.Q = Queue(maxsize=256)
        self.src = src
        self.cap = cv2.VideoCapture(self.src)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.grabbed, self.frame = self.cap.read()
        self.started = False

        # used to record the time at which we processed current frame
        self.new_frame_time = 0
        self.prev_frame_time = 0

        self.read_lock = Lock()

    def timestamp_frame(self, fr, fps):
        #fr = imutils.resize(fr, width=640)
        dt = str(datetime.datetime.now())
        cv2.putText(fr, "Queue Size: " + self.Q.qsize() + " FPS: " + fps, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(fr, dt, (390, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        return fr

    def set(self, var1, var2):
        self.cap.set(var1, var2)

    def start(self):
        if self.started:
            print('[!] Threaded video capturing has already been started.')
            return None
        self.started = True
        self.thread = Thread(target=self.update, args=())
        self.thread.start()
        return self

    def update(self):
        while self.started:
            grabbed, frame = self.cap.read()
            self.new_frame_time = time.time()

            # Calculating the fps

            # fps will be number of frame processed in given time frame
            # since their will be most of time error of 0.001 second
            # we will be subtracting it to get more accurate result
            fps = 1 / (self.new_frame_time - self.prev_frame_time)
            self.prev_frame_time = self.new_frame_time

            frame = self.timestamp_frame(frame, fps)

            self.Q.put(frame)
            with self.read_lock:
                self.grabbed = grabbed
                self.frame = frame

    def read(self):
        with self.read_lock:
            frame = self.Q.get()
            grabbed = self.grabbed
        return grabbed, frame

    def stop(self):
        self.started = False
        self.thread.join()

    def __exit__(self, exec_type, exc_value, traceback):
        self.cap.release()