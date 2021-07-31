# import the necessary packages
from util.face_cropper import FaceCropper
from threading import Thread
from collections import Counter

import requests, sys, os, shutil
import cv2
import datetime
import base64, json


def getBase64(image):
    with open(image, "rb") as img_file:
        img64 = base64.b64encode(img_file.read()).decode('utf-8')
    return img64


def image_resize(image, width=None, height=None, inter=cv2.INTER_AREA):
    # initialize the dimensions of the image to be resized and
    # grab the image size
    dim = None
    (h, w) = image.shape[:2]

    # if both the width and height are None, then return the
    # original image
    if width is None and height is None:
        return image

    # check to see if the width is None
    if width is None:
        # calculate the ratio of the height and construct the
        # dimensions
        r = height / float(h)
        dim = (int(w * r), height)

    # otherwise, the height is None
    else:
        # calculate the ratio of the width and construct the
        # dimensions
        r = width / float(w)
        dim = (width, int(h * r))

    # resize the image
    resized = cv2.resize(image, dim, interpolation=inter)

    # return the resized image
    return resized


class FrameReconFullFace:
    def __init__(self, path_todo='recon/todo/', path_cropped='recon/cropped/', path_not_cropped='recon/not_cropped/',
                 path_done='recon/done/'):
        # initialize the file video stream along with the boolean
        # used to indicate if the thread should be stopped or not
        self.stopped = False

        # frame to be cropped and recon
        self.frame = None

        # control flags
        self.last_token_date = None
        self.last_token = None
        self.video_source = None

        # incitialize paths
        self.path_todo = path_todo
        self.path_cropped = path_cropped
        self.path_not_cropped = path_not_cropped
        self.path_done = path_done

        self.recon_status = False
        self.last_recon_datetime = (datetime.datetime.now() - datetime.timedelta(hours=3))
        self.recon_retry = 0
        self.do_cropper = False

        # intialize thread
        self.thread = Thread(target=self.recognize, args=())
        self.thread.daemon = True

    def start(self):
        # start a thread to read frames from the file video stream
        self.thread.start()
        return self

    def set_frame(self, frame, video_source):
        self.frame = frame
        self.video_source = video_source

    def recognize(self):
        # keep looping infinitely
        imgBase64 = []
        self.insuficient_files_status = True
        while True:
            # verifica se existem frames para croppar
            if self.frame is not None:
                # inicia a data de recebimento do frame
                dtn = datetime.datetime.now()
                # monta o caminho para gravar o frame em todo
                to_recon_todo = self.path_todo + self.video_source.split('/')[-1] + "_" + dtn.strftime(
                    '%Y-%m-%d_%H_%M_%S_%f') + ".jpg"
                # grava o frame como arquivo
                cv2.imwrite(to_recon_todo, self.frame)
                print("[RECON] Frame saved at todo: " + to_recon_todo)

                if self.do_cropper == True:
                    # inicia o reconhecedor de faces para cropar
                    detecter = FaceCropper()

                    ## percorre apasta '/recon/todo' para cropar as faces encontradas
                    for filename in os.listdir(self.path_todo):
                        try:
                            if filename.endswith(".jpg"):
                                to_recon_todo = self.path_todo + filename

                                # pega o arquivo para cropaar as faces encontradas e carrega como resultado a qto encontrada,
                                # se não encontra faces, não cropamos mas copiamos o arquivo como não cropado para
                                result = detecter.generate(to_recon_todo, self.path_cropped, False)
                                if (result is not None) and (result > 0):
                                    print("[CROPPER] From: " + to_recon_todo + " To: " + self.path_cropped)
                                    shutil.move(to_recon_todo, self.path_done)
                                else:
                                    print("[CROPPER] From: " + to_recon_todo + " To: " + self.path_not_cropped)
                                    shutil.move(to_recon_todo, self.path_not_cropped)
                            else:
                                print("[CROPPER] Sem arquivos em: " + self.path_todo)
                            continue
                        except Exception:
                            print("[CROPPER] Deu merda! " + str(sys.exc_info()))
                self.frame = None

            # pega ao menos 6 dos frame original (not cropped), transforma para Base64
            for filename in os.listdir(self.path_todo):
                try:
                    if filename.endswith(".jpg") and len(imgBase64) <= 6:
                        # redimenciona antes de
                        imgBase64.append(getBase64(self.path_todo + filename))
                        # imgBase64.append(getBase64("../../recon/cropped/" + filename))
                        shutil.move(self.path_todo + filename, self.path_done + filename)
                        print("[RECON] Movendo de: " + (self.path_todo + filename) + " para: " + (
                                    self.path_done + filename))

                except Exception:
                    print("[E][RECON]" + str(sys.exc_info()))

            if len(imgBase64) > 4:
                print("[RECON] Starting RECON - DateTime: " + dtn.strftime('%Y-%m-%d_%H_%M_%S'))
                self.insuficient_files_status = False

                url = "http://www.fullfacelab.com/fffacerecognition_NC/autapi/users/authenticate"
                token = self.get_token()
                payload = json.dumps({
                    "projectName": "a94df8b7-90fd-49ac-9173-1f4da3782c6e",
                    "accessToken": token,
                    "keys": [],
                    "pictures": imgBase64
                })
                headers = {
                    'Content-Type': 'application/json'
                }
                try:
                    response = requests.request("POST", url, headers=headers, data=payload)
                    end_autenticate = datetime.datetime.now()
                    print("[RECON][Retorno Fullcace] Tempo: " + str((end_autenticate - dtn).total_seconds()))
                    print("[RECON][Retorno Fullcace] Resposta: " + response.text)
                    try:
                        if 'keys' in response.json():
                            # retorna uma lista (array) com pares de hash
                            recon = response.json()['keys']
                            # verifica se para cada item da lista a qtd de key cujo valor é 'nome'
                            recon_count = 0
                            for hash in recon:
                                recon_count = recon_count + len([k for k, v in hash.items() if v == 'nome'])

                            print("[RECON] Qtd keys 'nome' retornadas pela Fullface: " + str(recon_count))

                            # Chama a contagem para o frame
                            face_count = self.get_face_count(imgBase64[0], token)
                            print("[RECON][RESULTADO:] Reconhecidos:" + str(recon_count) + " - Contagem: " + str(face_count))
                            if (recon_count == face_count):
                                self.recon_status = True
                                self.last_recon_datetime = datetime.datetime.now()
                            else:
                                self.recon_status = False
                                print("[RECON] Nenhum reconhecimento no frame: " + str(len(recon)))
                        else:
                            print("[RECON][RESULTADO:]: " + str(self.recon_status))
                            self.recon_status = False
                    except Exception:
                        print("[E][RECON] frame_recon.py linhas 167 a 185" + str(sys.exc_info()))
                        self.recon_status = False
                except Exception:
                    print("[E][RECON] frame_recon.py linha 161" + str(sys.exc_info()))
                    self.recon_status = False
                if self.recon_status == False and self.recon_retry < 3:
                    self.recon_retry = self.recon_retry + 1
                    self.recon_status = True
                    print("[RECON][RETENTATIVA] : " + str(self.recon_retry))
                elif self.recon_status == False and self.recon_retry >= 3:
                    self.recon_retry = self.recon_retry + 1
                    # mantem o status false e cresce o num de retentativas
                    print("[RECON][RETENTATIVA] : " + str(self.recon_retry))
                else:
                    self.recon_retry = 0

                imgBase64 = []
            else:
                if self.insuficient_files_status != True:
                    print("[RECON] Qtd insuficiente para chamar reconhecimento. STATUS ATUAL: " + str(self.recon_status))
                    self.insuficient_files_status = True

    def get_token(self):
        if (self.last_token_date == None) or (datetime.datetime.now() - self.last_token_date).total_seconds() > 1190:
            url = "https://www.fullfacelab.com/fffacerecognition_NC/tokapi/token"

            payload = 'username=API_Testes&password=fullfaceAPITeste&grant_type=password&scope=a94df8b7-90fd-49ac-9173-1f4da3782c6e'
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            response = requests.request("POST", url, headers=headers, data=payload, verify=False)

            self.last_token = response.json()['access_token']

        return self.last_token

    def get_face_count(self, imgB64, access_token):
        import requests
        import json
        face_count = 0
        url = "http://fullfacelab.com/fffacerecognition_nc/qtdapi/users/faceCount"

        payload = json.dumps({
            "projectName": "a94df8b7-90fd-49ac-9173-1f4da3782c6e",
            "accessToken": access_token,
            "picture": imgB64
        })
        headers = {
            'Content-Type': 'application/json'
        }

        try:
            response = requests.request("POST", url, headers=headers, data=payload)
            face_count = response.json()['faceCount']
        except Exception:
            print("[E][COUNT_PEOPLE]" + str(sys.exc_info()))

        return face_count

    # Insufficient to have consumer use while(more()) which does
    # not take into account if the producer has reached end of
    # file stream.
    def running(self):
        return self.more() or not self.stopped

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True
        # wait until stream resources are released (producer thread might be still grabbing frame)
        self.thread.join()
