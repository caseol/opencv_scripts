import cv2

# carrega o modelo frontalface-default
faceCascade = cv2.CascadeClassifier("resources/haarcascades/haarcascade_frontalface_default.xml")
eyeCascade = cv2.CascadeClassifier("resources/haarcascades/haarcascade_eye.xml")

# lê a imagem que terá as faces identificadas
img = cv2.imread('resources/parque_da_cidade.jpg')
imgResize = cv2.resize(img,(640,480))

imgGray = cv2.cvtColor(imgResize, cv2.COLOR_RGB2GRAY)

faces = faceCascade.detectMultiScale(imgGray, 1.09, 3)

for (x, y, w, h) in faces:
    cv2.rectangle(imgResize, (x, y), (x + w, y + h), (255, 0, 0), 1, 4)

cv2.imshow("Resultado", imgResize)
cv2.waitKey(0)