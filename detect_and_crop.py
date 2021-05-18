import cv2
from util.face_cropper import FaceCropper

detecter = FaceCropper()
detecter.generate('resources/parque_da_cidade.jpg', 'output', False)
cv2.waitKey(0)