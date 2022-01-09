# import the necessary packages
from queue import Queue
from threading import Thread, Lock
import cv2
from vidgear.gears import CamGear
import time, datetime


class CountPeopleThread:
    def __init__(self, position="Não informado"):
        self.queue = Queue(maxsize=32)
        self.frame = None
        self.position = position
        self.stopped = False

        self.count = 0
        self.show = True

        self.isFace = False
        self.isProfile = False
        self.isEye = False

        self.faceCascade = cv2.CascadeClassifier("resources/haarcascades/haarcascade_frontalface_default.xml")
        self.profilefaceCascade = cv2.CascadeClassifier("resources/haarcascades/haarcascade_profileface.xml")
        self.eyeCascade = cv2.CascadeClassifier("resources/haarcascades/haarcascade_eye.xml")

        # intialize thread
        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True

    def start(self):
        # start a thread to read frames from the file video stream
        self.thread.start()
        return self

    def set_frame(self, frame):
        if frame is not None:
            self.queue.put(frame)

    def show_frame(self, on=True):
        self.show = on

    def update(self):
        frame_idx = 0
        last_sec = -1
        # keep looping infinitely
        while True:
            # if the thread indicator variable is set, stop the
            # thread
            if self.stopped:
                break
            #
            while self.queue.not_empty:
                contagem = 0
                _frame = self.queue.get()
                # _frame_gray = cv2.cvtColor(_frame, cv2.COLOR_RGB2GRAY)
                _frame_gray = _frame

                if _frame_gray is not None:
                    faces = self.faceCascade.detectMultiScale(_frame_gray, 1.2, 8, minSize=(35, 35))  # , minSize=(25, 25),flags=cv2.CASCADE_SCALE_IMAGE)
                    profileFaces = self.profilefaceCascade.detectMultiScale(_frame_gray, 1.1, 9, minSize=(35, 35))  # , minSize=(25, 25),flags=cv2.CASCADE_SCALE_IMAGE)
                    eyes = self.eyeCascade.detectMultiScale(_frame_gray, 1.2, 8, minSize=(35, 35))

                    if len(faces) > 0:
                        if self.show:
                            for (x, y, w, h) in faces:
                                cv2.rectangle(_frame, (x, y), (x + w, y + h), (255, 0, 0), 1, 4)
                        contagem = len(faces)
                    elif len(profileFaces) > 0:
                        if self.show:
                            for (x, y, w, h) in profileFaces:
                                cv2.rectangle(_frame, (x, y), (x + w, y + h), (0, 255, 0), 1, 4)
                        contagem = len(profileFaces)
                    elif len(eyes) > 0:
                        if self.show:
                            for (x, y, w, h) in eyes:
                                cv2.rectangle(_frame, (x, y), (x + w, y + h), (0, 0, 255), 1, 4)
                        contagem = len(eyes)
                    self.frame = _frame
                    cv2.putText(_frame, "Contagem: " + str(contagem > 0), (5, 360), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    self.count = contagem

