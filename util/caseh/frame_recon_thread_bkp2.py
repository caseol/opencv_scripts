from threading import Thread
from queue import Queue
import cv2
import time
import datetime
import face_recognition
import pickle
import sys
import shutil
import pysftp


class FrameReconThread(object):
    def __init__(self, path_todo='recon/todo/', path_cropped='recon/cropped/', path_not_cropped='recon/not_cropped/',
                 path_done='recon/done/', max_retry=3):
        # flag control
        self.stopped = True
        self.dt = datetime.datetime.now()
        self.queue = Queue(maxsize=128)
        self.data = pickle.loads(open("resources/encodings.pickle", "rb").read())
        self.detector = cv2.CascadeClassifier("resources/haarcascade_frontalface_default.xml")

        # credenciais para acesso a cloud
        self.host = "api.orbis.net.br"
        self.pem_file = '~/.ssh/authorized_keys/orbisicar.pem'

        # inicializa variável do frame
        self.final_frame = None
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
        self.stopped = False
        self.thread.start()
        return self

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True
        # wait until stream resources are released (producer thread might be still grabbing frame)
        self.thread.join()

    def update_model(self):

        # verifica se existe modelo para baixar
        try:
            print("[INFO] Verificando a Cloud...")
            with pysftp.Connection(self.host, username='ubuntu', private_key=self.pem_file) as sftp:
                if sftp.exists("/home/ubuntu/railsapp/orbis_proxy/public/modelos/encodings.pickle"):
                    file = sftp.get("/home/ubuntu/railsapp/orbis_proxy/public/modelos/encodings.pickle", "resources/encodings.pickle")
                    sftp.remove("/home/ubuntu/railsapp/orbis_proxy/public/modelos/encodings.pickle")
                    self.data = pickle.loads(open("resources/encodings.pickle", "rb").read())
                    print("[DOWNLOADER] NOVO MODELO BAIXADO! ")
                else:
                    print("[DOWNLOADER] Sem modelos novos! ")
        except Exception:
            print("[UPLOADER] Deu merda! " + str(sys.exc_info()))
        # self.detector = cv2.CascadeClassifier("")


    def set_frame(self, frame):
        # self.frames.append(frame)
            self.queue.put(frame)
        # Resize frame of video to   1/4 size for faster face recognition processing
        #self.small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

    def recon_frame(self):
        # Read the next frame from the stream in a different thread
        last_minute = -1
        while True:
            dtn = datetime.datetime.now()
            # if the thread indicator variable is set, stop the thread
            if self.stopped:
                break

            print("TAMANHO FILA: " +str(self.queue.qsize()))

            while self.queue.not_empty:
                frame = self.queue.get()
                recon_false = []
                recon_true = []
                # COMEÇA O RECON AQUI
                # convert the input frame from (1) BGR to grayscale (for face
                # detection) and (2) from BGR to RGB (for face recognition)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # detecta faces no frame em grayscale
                rects = self.detector.detectMultiScale(gray, scaleFactor=1.1,
                                                  minNeighbors=6, minSize=(40, 40),
                                                  flags=cv2.CASCADE_SCALE_IMAGE)
                contador = str(rects.shape[0])

                # OpenCV returna as coordenadas da box no formato (x, y, w, h)
                # mas precisamos delas no formato (top, right, bottom, left), então
                # precisamos reordenar as coordenadas
                boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]


                # calcula os encodings/pontos para cada face nas boxes para comparar com o modelo
                encodings = face_recognition.face_encodings(rgb, boxes)
                # fim da detecção de faces

                # quantidade de faces encontradas
                names = []
                self.count = len(encodings)

                # loop sobre cada enconding encontrado e compara com o modelo
                for encoding in encodings:
                    # tenta dar match de cada face com o modelo
                    # modelo = data["encodings"]
                    matches = face_recognition.compare_faces(self.data["encodings"],
                                                             encoding, 0.4)
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

                for ((top, right, bottom, left), name) in zip(boxes, names):
                    # draw the predicted face name on the image
                    if name == "Desconhecido":
                        recon_false.append(name)
                        # cor vermelha
                        _color = (0, 0, 255)
                    else:
                        recon_true.append(name)
                        # cor verde
                        _color = (0, 255, 0)

                    cv2.rectangle(frame, (left, top), (right, bottom),
                                  _color, 2)
                    y = top - 15 if top - 15 > 15 else top + 15
                    cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
                                0.75, _color, 2)
                self.final_frame = frame

                # temos que sumarizar os frames para poder extrair a contagem e o reconhecimento
                # self.count_recon = names.count()
                if len(recon_false) > len(recon_true) or len(recon_true) == 0:
                    self.recon_status = False
                    self.recon_retry = self.recon_retry + 1
                    print("NÃO RECONHECIDO!")
                else:
                    # informa horário do último reconhecimento
                    self.last_recon_datetime = datetime.datetime.now()
                    self.recon_status = True
                    self.recon_retry = 0
                    print("RECONHECIDO!!!")
            else:
                time.sleep(0.2)  # Rest for 10ms, we have a full queue