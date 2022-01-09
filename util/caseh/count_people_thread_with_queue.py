# import the necessary packages
from queue import Queue
from threading import Thread, Lock
import numpy as np
import cv2
import imutils
from vidgear.gears import CamGear
import time, datetime

class CountPeopleThread:
    def __init__(self, position="Não informado", onlyDetect=False, confidence=0.6, queue_out=Queue(maxsize=128)):
        self.queue_in = Queue(maxsize=32)
        self.queue_out = queue_out
        self.frame = None
        self.face_out = None
        self.position = position
        self.confidence = confidence

        self.stopped = False
        self.onlyDetect = onlyDetect
        self.detected = False

        self.count = 0
        self.show = True

        self.isFace = False
        self.isProfile = False
        self.isEye = False

        print("[INFO] loading model...")
        self.net = cv2.dnn.readNetFromCaffe('resources/face_detect_model/deploy.prototxt.txt', 'resources/face_detect_model/res10_300x300_ssd_iter_140000.caffemodel')

        # intialize thread
        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True
        self.read_lock = Lock()

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True

    def start(self):
        # start a thread to read frames from the file video stream
        self.thread.start()
        return self

    def set_frame(self, frame):
        if frame is not None:
            self.queue_in.put(frame)

    def show_frame(self, on=True):
        self.show = on

    def update(self):
        frame_idx = 0
        last_sec = -1
        # keep looping infinitely
        while True:
            # se a flag estiver ativada, para a
            # thread
            if self.stopped:
                break
            #
            while self.queue_in.not_empty:
                _frame = self.queue_in.get()
                # pega as dimensões do frame e converte para um blob

                _detections = 0
                if _frame is not None:
                    (h, w) = _frame.shape[:2]
                    # blob = cv2.dnn.blobFromImage(cv2.resize(_frame, (300, 300)), 1.0,
                    blob = cv2.dnn.blobFromImage(cv2.resize(_frame, (300, 300)), 1.0,
                                                 (300, 300), (104.0, 177.0, 123.0))
                    self.net.setInput(blob)
                    detections = self.net.forward()
                    face_crop = None
                    # loop sobre as detecções
                    for i in range(0, detections.shape[2]):
                        # extrai o nível de confiança na detecção (probabilidade associada a predição)
                        confidence = detections[0, 0, i, 2]

                        # filtra detecções fracas abaixo do nível de confiança especificado
                        # o valor default é 0.6 (60%)
                        if confidence < self.confidence:
                            continue

                        # contador de detecções
                        _detections = _detections + 1
                        # calcula as coordenadas (x, y) do bounding box para a
                        # detecção
                        box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                        (startX, startY, endX, endY) = box.astype("int")

                        # desenha o bounding box da face encontrada junto com a probabilidade
                        # probability
                        text = "{:.2f}%".format(confidence * 100)
                        num = "ID: " + str(int(i) + 1)
                        y = startY - 10 if startY - 10 > 10 else startY + 10
                        cv2.rectangle(_frame, (startX, startY), (endX, endY),
                                      (0, 0, 255), 2)

                        # image[Y_start: Y_end, X_start: X_end]
                        # face_crop = _frame[startY:endY, startX:endX]
                        # if self.queue_out.not_full:
                        #    print('Inclui nova face croppada')
                            # self.queue_out.put(face_crop)
                        # self.face_out = face_crop

                        cv2.putText(_frame, num, (startX, y),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)
                        cv2.putText(_frame, text, (startX + 50, y),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)

                    # define o número da contagem de acordo com o número de boxes definidos
                    self.count = _detections

                    self.frame = _frame
                    self.detected = self.count > 0
                    if self.onlyDetect:
                        cv2.putText(_frame, "Contagem: " + str(self.count > 0), (5, 360), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    else:
                        cv2.putText(_frame, "Contagem: " + str(self.count), (5, 360), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

