import cv2

# carrega o modelo frontalface-default
faceCascade = cv2.CascadeClassifier("resources/haarcascades/haarcascade_frontalface_alt_tree.xml")
eyeCascade = cv2.CascadeClassifier("resources/haarcascades/haarcascade_eye.xml")

# lê a imagem que terá as faces identificadas
# img = cv2.imread('resources/parque_da_cidade.jpg')

# video_capture = cv2.VideoCapture('/dev/video0')
video_capture = cv2.VideoCapture('')

while True:
    ret, frame = video_capture.read()
    if ret:
        imgResize = cv2.resize(frame,(640,480))

    imgGray = cv2.cvtColor(imgResize, cv2.COLOR_RGB2GRAY)

    faces = faceCascade.detectMultiScale(imgGray, 1.1, 6)

    for (x, y, w, h) in faces:
        cv2.rectangle(imgResize, (x, y), (x + w, y + h), (255, 0, 0), 1, 4)

    cv2.imshow("Resultado", imgResize)
    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break