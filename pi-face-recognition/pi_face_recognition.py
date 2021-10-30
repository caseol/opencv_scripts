# USAGE
# python pi_face_recognition.py --cascade haarcascade_frontalface_default.xml --encodings encodings.pickle

# import the necessary packages
from imutils.video import VideoStream
from imutils.video import FPS
import face_recognition
import argparse
import imutils
import pickle
import time
import cv2

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--cascade", required=True,
	help = "path to where the face cascade resides")
ap.add_argument("-e", "--encodings", required=True,
	help="path to serialized db of facial encodings")
args = vars(ap.parse_args())

# load the known faces and embeddings along with OpenCV's Haar
# cascade for face detection
print("[INFO] carregando modelos + hog face detector...")
data = pickle.loads(open(args["encodings"], "rb").read())
detector = cv2.CascadeClassifier(args["cascade"])

# initialize the video stream and allow the camera sensor to warm up
print("[INFO] starting video stream...")
vs = VideoStream(src=0).start()
# vs = VideoStream(usePiCamera=True).start()
time.sleep(2.0)

# start the FPS counter
fps = FPS().start()

# loop over frames from the video file stream
while True:
	# grab the frame from the threaded video stream and resize it
	# to 500px (to speedup processing)
	frame = vs.read()
	if frame.any():
		frame = imutils.resize(frame, width=500)

		# converte o frame: (1) BGR para escala de cinza (para detectar
		# a face) and (2) de BGR to RGB (para o reconhecimento da face)
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

		# detecta faces no frame em grayscale
		rects = detector.detectMultiScale(gray, scaleFactor=1.1,
			minNeighbors=5, minSize=(30, 30),
			flags=cv2.CASCADE_SCALE_IMAGE)

		# OpenCV returna as coordenadas da box no formato (x, y, w, h)
		# mas precisamos delas no formato (top, right, bottom, left), então
		# precisamos reordenar as coordenadas
		boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]

		# calcula os encodings/pontos para cada face na box de acordo com o modelo
		encodings = face_recognition.face_encodings(rgb, boxes)
		names = []

		# loop sobre os pontos dos modelos
		for encoding in encodings:
			# tenta dar match de cada face com o modelo
			# modelo = data["encodings"]
			matches = face_recognition.compare_faces(data["encodings"],
				encoding)
			name = "Desconhecido"

			# verifica se tem os pontos
			if True in matches:
				# find the indexes of all matched faces then initialize a
				# dictionary to count the total number of times each face
				# was matched
				matchedIdxs = [i for (i, b) in enumerate(matches) if b]
				counts = {}

				# loop sobre os index encontrados e mantém a conta para cada face reconhecida
				#
				for i in matchedIdxs:
					name = data["names"][i]
					counts[name] = counts.get(name, 0) + 1

				# determina a face reconhecida de acordo com o maior número
				# de votos (obs: caso um improvável empate nos votos será
				# selecionado a primeira entrada no dicionário de modelos)
				name = max(counts, key=counts.get)

			# atualiza a list de nomes
			names.append(name)

		# loop sobre as faces reconhecidas
		for ((top, right, bottom, left), name) in zip(boxes, names):
			# draw the predicted face name on the image
			if name == "Desconhecido":
				# cor vermelha
				_color = (0, 0, 255)
			else:
				# cor verde
				_color = (0, 255, 0)

			cv2.rectangle(frame, (left, top), (right, bottom),
				_color, 2)
			y = top - 15 if top - 15 > 15 else top + 15
			cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
				0.75, _color, 2)

		# mostra a image na tela
		cv2.imshow("Frame", frame)
		key = cv2.waitKey(1) & 0xFF

		# se pressionar `q`, para o loop
		if key == ord("q"):
			break

		# update the FPS counter
		fps.update()

# stop the timer and display FPS information
fps.stop()
print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()