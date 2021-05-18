from time import sleep

import cv2

# initialize the camera
cam = cv2.VideoCapture(0)
cam2 = cv2.VideoCapture(1)
sleep(2)
ret, image = cam.read()
ret2, image2 = cam2.read()

print(ret)
print(ret2)

cv2.waitKey(0)

if ret:
    cv2.imshow('CAM 1', image)
    cv2.waitKey(0)
    cv2.destroyWindow('CAM 1')
    cv2.imwrite('/home/coliveira/Workspace/Python/OpenCVScripts/output', image)

if ret2:
    cv2.imshow('SnapshotTest', image2)
    cv2.waitKey(0)
    cv2.destroyWindow('CAM 2')
    cv2.imwrite('/home/coliveira/Workspace/Python/OpenCVScripts/output', image2)

cam.release()
cam2.release()