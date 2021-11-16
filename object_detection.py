import cv2

# carrega o modelo frontalface-default

faceCascade = cv2.CascadeClassifier("resources/haarcascades/haarcascade_frontalface_alt_tree.xml")
eyeCascade = cv2.CascadeClassifier("resources/haarcascades/haarcascade_eye.xml")
upperBody = cv2.CascadeClassifier("resources/haarcascades/haarcascade_upperbody.xml")

# lê a imagem que terá as faces identificadas
# img = cv2.imread('resources/parque_da_cidade.jpg')

# video_capture = cv2.VideoCapture('/dev/video0')
video_capture = cv2.VideoCapture('output/monit_2021-11-13_17_55_inv.avi')

while True:
    ret, frame = video_capture.read()
    if ret:
        imgResize = cv2.resize(frame,(640,480))

    imgGray = cv2.cvtColor(imgResize, cv2.COLOR_RGB2GRAY)

    faces = faceCascade.detectMultiScale(imgGray, 1.1, 6)
    eyes = eyeCascade.detectMultiScale(imgGray, 1.1, 6)
    upper_body = upperBody.detectMultiScale(
        imgGray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(50, 75),  # Min size for valid detection, changes according to video size or body size in the video.
        flags=cv2.CASCADE_SCALE_IMAGE
    )

    for (x, y, w, h) in upper_body:
        cv2.rectangle(imgResize, (x, y), (x + w, y + h), (0, 255, 0), 1)  # creates green color rectangle with a thickness size of 1
        cv2.putText(imgResize, "Upper Body Detected", (x + 5, y + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)  # creates green color text with text size of 0.5 & thickness size of 2

    #for (x, y, w, h) in faces:
    #    cv2.rectangle(imgResize, (x, y), (x + w, y + h), (255, 0, 0), 1, 4)
    #for (x, y, w, h) in eyes:
    #    cv2.rectangle(imgResize, (x, y), (x + w, y + h), (255, 0, 0), 1, 4)

    cv2.imshow("Resultado", imgResize)
    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break