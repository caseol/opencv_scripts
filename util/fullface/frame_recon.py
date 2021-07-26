# import the necessary packages
from util.face_cropper import FaceCropper
from threading import Thread
import requests, sys, os, shutil
import cv2
import datetime


class FrameReconFullFace:
    def __init__(self, path_todo='recon/todo/', path_cropped='recon/cropped/', path_not_cropped='recon/not_cropped/' , path_done='recon/done/'):
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
        self.recon_retry = 0

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
        while True:
            # verifica se existem frames para croppar
            if self.frame is not None:
                # inicia a data de recebimento do frame
                dtn = datetime.datetime.now()
                # monta o caminho para gravar o frame em todo
                to_recon_todo = self.path_todo + self.video_source.split('/')[-1] + "_" + dtn.strftime('%Y-%m-%d_%H_%M_%S_%f') + ".jpg"
                # grava o frame como arquivo
                cv2.imwrite(to_recon_todo, self.frame)
                print("[RECON] Frame saved at todo: " + to_recon_todo)

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
                        print("[CROPPER] Deu merda! " +  str(sys.exc_info()))
                self.frame = None

    def get_token(self):
        if (self.last_token_date == None) or (datetime.datetime.now() - self.last_token_date).total_seconds() > 1190:
            url = "https://www.fullfacelab.com/fffacerecognition_NC/tokapi/token"

            payload = 'username=API_Testes&password=fullfaceAPITeste&grant_type=password&scope=a94df8b7-90fd-49ac-9173-1f4da3782c6e'
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            response = requests.request("POST", url, headers=headers, data=payload)
            return response.json()

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
