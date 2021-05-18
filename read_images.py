import cv2
# LOAD AN IMAGE USING 'IMREAD'
img = cv2.imread("/home/coliveira/Documents/fotos/parque_da_cidade.jpg")
imgResize = cv2.resize(img,(640,480))
print(imgResize.shape)
# DISPLAY
cv2.imshow("Parque da Cidade",imgResize)
cv2.waitKey(0)