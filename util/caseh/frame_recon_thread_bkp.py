from threading import Thread
from queue import Queue
import cv2
import datetime
import face_recognition
import pickle


class FrameReconThread(object):
    def __init__(self, path_todo='recon/todo/', path_cropped='recon/cropped/', path_not_cropped='recon/not_cropped/',
                 path_done='recon/done/', max_retry=3):
        # flag control
        self.stopped = True
        self.dt = datetime.datetime.now()
        self.queue = Queue(maxsize=512)
        self.data = pickle.loads(open("resources/encodings.pickle", "rb").read())
        self.detector = cv2.CascadeClassifier("resources/haarcascade_frontalface_default.xml")

        # inicializa variável do frame
        self.frames = []
        self.recon_frames = []
        self.small_frame = 0

        # incitialize paths
        self.path_todo = path_todo
        self.path_cropped = path_cropped
        self.path_not_cropped = path_not_cropped
        self.path_done = path_done

        # atributos de recon
        self.recon_status = False
        self.count = 0
        self.count_recon = 0

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
        self.stopped = False
        return self

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True
        # wait until stream resources are released (producer thread might be still grabbing frame)
        self.thread.join()

    def set_frame(self, frame):
        self.frames.append(frame)
        # Resize frame of video to   1/4 size for faster face recognition processing
        #self.small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

    def recon_frame(self):
        # Read the next frame from the stream in a different thread
        last_minute = -1
        recon_true = []
        recon_false = []
        while True:
            dtn = datetime.datetime.now()
            # if the thread indicator variable is set, stop the thread
            if self.stopped:
                break

            for frame in self.frames:
                # FAZ O RECON AQUI
                # convert the input frame from (1) BGR to grayscale (for face
                # detection) and (2) from BGR to RGB (for face recognition)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # detecta faces no frame em grayscale
                rects = self.detector.detectMultiScale(gray, scaleFactor=1.1,
                                                  minNeighbors=6, minSize=(30, 30),
                                                  flags=cv2.CASCADE_SCALE_IMAGE)

                # OpenCV returna as coordenadas da box no formato (x, y, w, h)
                # mas precisamos delas no formato (top, right, bottom, left), então
                # precisamos reordenar as coordenadas
                boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]

                # calcula os encodings/pontos para cada face na box de acordo com o modelo
                encodings = face_recognition.face_encodings(rgb, boxes)
                names = []

                # loop sobre os pontos dos modelos
                self.count = len(encodings)
                for encoding in encodings:
                    # tenta dar match de cada face com o modelo
                    # modelo = data["encodings"]
                    matches = face_recognition.compare_faces(self.data["encodings"],
                                                             encoding)
                    name = "Desconhecido"

                    # verifica se tem match no reconhecimento
                    if True in matches:
                        # pega os indices de todas as faces encontradas e inicializa
                        # o dicionario com a contagem total do numero de vezes que cada face
                        # foi encontrada
                        matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                        counts = {}

                        # loop sobre os index encontrados e mantém a conta para cada face reconhecida
                        #
                        for i in matchedIdxs:
                            name = self.data["names"][i]
                            counts[name] = counts.get(name, 0) + 1

                        # determina a face reconhecida de acordo com o maior número
                        # de votos (obs: caso um improvável empate nos votos será
                        # selecionado a primeira entrada no dicionário de modelos)
                        name = max(counts, key=counts.get)

                    # atualiza a list de nomes
                    names.append(name)

                # loop sobre as faces reconhecidas
                for ((top, right, bottom, left), name) in zip(boxes, names):
                    if name == "Desconhecido":
                        recon_false.append(name)
                        # desenha em vermelho
                        # draw the predicted face name on the image
                        cv2.rectangle(frame, (left, top), (right, bottom),
                                      (0, 0, 255), 2)
                        y = top - 15 if top - 15 > 15 else top + 15
                        cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
                                    0.75, (0, 0, 255), 2)
                    else:
                        recon_true.append(name)
                        # draw the predicted face name on the image
                        cv2.rectangle(frame, (left, top), (right, bottom),
                                      (0, 255, 0), 2)
                        y = top - 15 if top - 15 > 15 else top + 15
                        cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
                                    0.75, (0, 255, 0), 2)

                # disponibiliza o recon na thread principal
                self.queue.put(frame)
                if self.stopped:
                    break

            # limpa o array de frames para recon
            self.frames.clear()

            # self.count_recon = names.count()
            if len(recon_false) >= len(recon_true) or len(recon_true) == 0:
                self.recon_status = False
                self.recon_retry = self.recon_retry + 1
                print("NÃO RECONHECIDO!")
            else:
                # informa horário do último reconhecimento
                self.last_recon_datetime = datetime.datetime.now()
                self.recon_status = True
                self.recon_retry = 0
                print("RECONHECIDO!!!")