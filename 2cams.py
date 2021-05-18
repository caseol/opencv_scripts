import cv2
#cap0 = cv2.VideoCapture(0)
cap1 = cv2.VideoCapture(1)
#ret0, frame0 = cap0.read()
#assert ret0
ret1, frame1 = cap1.read()
assert ret1 # now it works?!