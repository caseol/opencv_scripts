import cv2, sys

class FaceCropper(object):

    CASCADE_PATH = "resources/haarcascades/haarcascade_frontalface_default.xml"

    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(self.CASCADE_PATH)

    def generate(self, image_path, output_path, show_result= False):
        try:
            img = cv2.imread(image_path)
            if (img is None):
                print('[RECON] Não foi possível abrir a imagem %s' % image_path)
                return 0
        except Exception:
            print('[CROPPER] Deu ruim! %s' % sys.exc_info())

        img_bg = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        try:
            faces = self.face_cascade.detectMultiScale(img_bg, 1.1, 3, minSize=(120, 120))
            if (faces is None):
                print('[RECON] Falhou ao tentar detectar alguma face em %s ' % image_path)
                return 0

            if (show_result):
                for (x, y, w, h) in faces:
                    cv2.rectangle(img, (x,y), (x+w, y+h), (255,0,0), 2)
                cv2.imshow('img', img)
                cv2.waitKey(0)
                cv2.destroyAllWindows()

            facecnt = len(faces)
            print("[RECON] Qtd detectada: " + str(facecnt) + " em  " + image_path)
            i = 0
            height, width = img.shape[:2]

            for (x, y, w, h) in faces:
                r = max(w, h) / 2
                centerx = x + w / 2
                centery = y + h / 2
                nx = int(centerx - r)
                ny = int(centery - r)
                nr = int(r * 2)

                faceimg = img[ny:ny+nr, nx:nx+nr]
                lastimg = cv2.resize(faceimg, (256, 256))
                i += 1
                # cv2.imwrite("output/image%d.jpg" % i, lastimg)
                result = cv2.imwrite(str(output_path) + "/cropped_" + image_path.split('/')[2].split('.')[0] + "_" + str(i) + ".jpg", lastimg)
                print('[RECON] Result: %s' % result)
        except Exception:
            print('[RECON] Deu muita merda! %s' % sys.exc_info())