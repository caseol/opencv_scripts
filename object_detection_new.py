import cv2
import time
from util.caseh.count_people_thread import CountPeopleThread
from util.caseh.detect_people_thread import DetectPeopleThread

# carrega o modelo frontalface-default

# faceCascade = cv2.CascadeClassifier("resources/haarcascades/haarcascade_frontalface_default.xml")
# profilefaceCascade = cv2.CascadeClassifier("resources/haarcascades/haarcascade_profileface.xml")
# eyeCascade = cv2.CascadeClassifier("resources/haarcascades/haarcascade_eye.xml")
# upperBody = cv2.CascadeClassifier("resources/haarcascades/haarcascade_upperbody.xml")

# lê a imagem que terá as faces identificadas
# img = cv2.imread('resources/parque_da_cidade.jpg')

# video_capture = cv2.VideoCapture('/dev/video0')

# video_capture = cv2.VideoCapture('videos_teste/rasp4b/monit_2021-11-13_18_00.avi')
# video_capture = cv2.VideoCapture('videos_teste/rasp4b/uploaded/monit_2021-11-13_17_45.avi')
# video_capture = cv2.VideoCapture('videos_teste/rasp3bplus/monit_2021-11-17_15_55.avi')

vs_back = cv2.VideoCapture('videos_novos/monit_2021-11-20_17_45.avi')
vs_front = cv2.VideoCapture('videos_novos/recon_2021-11-20_17_50.avi')

# video_capture = cv2.VideoCapture('/home/coliveira/Workspace/Python/OpenCVScripts/videos_teste/monit/traseiro/videos/monit_2021-11-18_17_00.avi')
contagem = 0

count_traseiro_direito = CountPeopleThread('traseiro_direito').start()
count_frente_direito = CountPeopleThread('frente_meio').start()
count_frente_esquerdo = CountPeopleThread('frente_esquerdo').start()

while True:
    ret_front, frame_front = vs_front.read()
    ret_back, frame_back = vs_back.read()
    # frame = cv2.flip(frame, -1)

    if ret_front:
        imgResize = cv2.resize(frame_front,(640,480))
        # image[Y_start: Y_end, X_start: X_end]

        count_frente_esquerdo = imgResize[0:380, 0:200]  # Crop from {x, y, w, h } => {0, 0, 300, 400}
        # cv2.imshow("Traseiro direito", crop_traseiro_direito)

        crop_traseiro_meio = imgResize[0:380, 220:410]  # Crop from {x, y, w, h } => {0, 0, 300, 400}
        # cv2.imshow("Traseiro Meio", crop_traseiro_meio)

        crop_traseiro_esquerdo = imgResize[0:380, 430:640]  # Crop from {x, y, w, h } => {0, 0, 300, 400}
        # cv2.imshow("Traseiro ESquerdo", crop_traseiro_esquerdo)

        count_traseiro_direito.set_frame(crop_traseiro_direito)
        print("Contagem traseiro direito: " + str(count_traseiro_direito.count))
        count_traseiro_meio.set_frame(crop_traseiro_meio)
        print("Contagem traseiro meio: " + str(count_traseiro_meio.count))
        count_traseiro_esquerdo.set_frame(crop_traseiro_esquerdo)
        print("Contagem traseiro direito: " + str(count_traseiro_esquerdo.count))

        _count_traseiro_esquerdo = count_traseiro_esquerdo.frame
        _count_traseiro_meio = count_traseiro_meio.frame
        _count_traseiro_direito = count_traseiro_direito.frame

        if _count_traseiro_esquerdo is not None:
            cv2.imshow("Traseiro esquerdo", _count_traseiro_esquerdo)
        if _count_traseiro_meio is not None:
            cv2.imshow("Traseiro meio", _count_traseiro_meio)
        if _count_traseiro_direito is not None:
            cv2.imshow("Traseiro direito", _count_traseiro_direito)

        # imgGray = cv2.cvtColor(crop_traseiro_direito, cv2.COLOR_RGB2GRAY)
        # imgGray2 = cv2.cvtColor(crop_traseiro_esquerdo, cv2.COLOR_RGB2GRAY)
        # imgGray3 = cv2.cvtColor(crop_traseiro_meio, cv2.COLOR_RGB2GRAY)

        # faces = faceCascade.detectMultiScale(imgGray, 1.1, 12, minSize=(35, 35)) #, minSize=(25, 25),flags=cv2.CASCADE_SCALE_IMAGE)
        # profileFaces = profilefaceCascade.detectMultiScale(imgGray, 1.2, 9, minSize=(35, 35)) #, minSize=(25, 25),flags=cv2.CASCADE_SCALE_IMAGE)
        # eyes = eyeCascade.detectMultiScale(imgGray, 1.1, 12, minSize=(35, 35))

        # faces2 = faceCascade.detectMultiScale(imgGray2, 1.1, 12, minSize=(25, 25))  # , minSize=(25, 25),flags=cv2.CASCADE_SCALE_IMAGE)
        # profileFaces2 = profilefaceCascade.detectMultiScale(imgGray2, 1.2, 9, minSize=(25, 25))  # , minSize=(25, 25),flags=cv2.CASCADE_SCALE_IMAGE)
        # eyes2 = eyeCascade.detectMultiScale(imgGray2, 1.1, 12, minSize=(35, 35))

        # faces3 = faceCascade.detectMultiScale(imgGray3, 1.1, 12, minSize=(25, 25))  # , minSize=(25, 25),flags=cv2.CASCADE_SCALE_IMAGE)
        # profileFaces3 = profilefaceCascade.detectMultiScale(imgGray3, 1.1, 9, minSize=(25, 25))  # , minSize=(25, 25),flags=cv2.CASCADE_SCALE_IMAGE)
        # eyes3 = eyeCascade.detectMultiScale(imgGray3, 1.1, 12, minSize=(35, 35))

        # contagem= 0
        # contagem2= 0
        # contagem3 = 0

        #if len(faces) > 0:
        #    for (x, y, w, h) in faces:
        #        cv2.rectangle(crop_traseiro_direito, (x, y), (x + w, y + h), (255, 0, 0), 1, 4)
        #    contagem = len(faces)
        #elif len(profileFaces) > 0:
        #    for (x, y, w, h) in profileFaces:
        #        cv2.rectangle(crop_traseiro_direito, (x, y), (x + w, y + h), (0, 255, 0), 1, 4)
        #    contagem = len(profileFaces)
        #elif len(eyes) > 0:
        #    for (x, y, w, h) in eyes:
        #        cv2.rectangle(crop_traseiro_direito, (x, y), (x + w, y + h), (0, 0, 255), 1, 4)
        #    contagem = len(eyes)

        #if len(faces2) > 0:
        #    for (x, y, w, h) in faces2:
        #        cv2.rectangle(crop_traseiro_esquerdo, (x, y), (x + w, y + h), (255, 0, 0), 1, 4)
        #    contagem2 = len(faces2)
        #elif len(profileFaces2) > 0:
        #    for (x, y, w, h) in profileFaces2:
        #        cv2.rectangle(crop_traseiro_esquerdo, (x, y), (x + w, y + h), (0, 255, 0), 1, 4)
        #    contagem2 = len(profileFaces2)
        #elif len(eyes2) > 0:
        #    for (x, y, w, h) in eyes2:
        #        cv2.rectangle(crop_traseiro_esquerdo, (x, y), (x + w, y + h), (0, 0, 255), 2, 4)
        #    contagem2 = len(eyes2)

        #if len(faces3) > 0:
        #    for (x, y, w, h) in faces3:
        #        cv2.rectangle(crop_traseiro_meio, (x, y), (x + w, y + h), (255, 0, 0), 1, 4)
        #    contagem3 = len(faces3)
        #elif len(profileFaces3) > 0:
        #    for (x, y, w, h) in profileFaces2:
        #        cv2.rectangle(crop_traseiro_meio, (x, y), (x + w, y + h), (0, 255, 0), 1, 4)
        #    contagem3 = len(faces3)
        #elif len(eyes3) > 0:
        #    for (x, y, w, h) in eyes3:
        #        cv2.rectangle(crop_traseiro_meio, (x, y), (x + w, y + h), (0, 0, 255), 2, 4)
        #    contagem3 = len(eyes3)

        #cv2.putText(imgResize, "Contagem 1: " + str(contagem), (5, 400), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        #cv2.putText(imgResize, "Contagem 2: " + str(contagem2), (15, 400), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        #cv2.putText(imgResize, "Contagem 3: " + str(contagem3), (25, 400), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        #cv2.imshow("Traseiro direito", crop_traseiro_direito)
        #cv2.imshow("Traseiro esquerdo", crop_traseiro_esquerdo)
        #cv2.imshow("Traseiro meio", crop_traseiro_meio)
        #cv2.imshow("Contagem: ", imgResize)

    if ret_back:
        imgResize = cv2.resize(frame,(640,480))
        # image[Y_start: Y_end, X_start: X_end]

        crop_traseiro_direito = imgResize[0:380, 0:200]  # Crop from {x, y, w, h } => {0, 0, 300, 400}
        # cv2.imshow("Traseiro direito", crop_traseiro_direito)

        crop_traseiro_meio = imgResize[0:380, 220:410]  # Crop from {x, y, w, h } => {0, 0, 300, 400}
        # cv2.imshow("Traseiro Meio", crop_traseiro_meio)

        crop_traseiro_esquerdo = imgResize[0:380, 430:640]  # Crop from {x, y, w, h } => {0, 0, 300, 400}
        # cv2.imshow("Traseiro ESquerdo", crop_traseiro_esquerdo)

        count_traseiro_direito.set_frame(crop_traseiro_direito)
        print("Contagem traseiro direito: " + str(count_traseiro_direito.count))
        count_traseiro_meio.set_frame(crop_traseiro_meio)
        print("Contagem traseiro meio: " + str(count_traseiro_meio.count))
        count_traseiro_esquerdo.set_frame(crop_traseiro_esquerdo)
        print("Contagem traseiro direito: " + str(count_traseiro_esquerdo.count))

        _count_traseiro_esquerdo = count_traseiro_esquerdo.frame
        _count_traseiro_meio = count_traseiro_meio.frame
        _count_traseiro_direito = count_traseiro_direito.frame

        if _count_traseiro_esquerdo is not None:
            cv2.imshow("Traseiro esquerdo", _count_traseiro_esquerdo)
        if _count_traseiro_meio is not None:
            cv2.imshow("Traseiro meio", _count_traseiro_meio)
        if _count_traseiro_direito is not None:
            cv2.imshow("Traseiro direito", _count_traseiro_direito)

    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break