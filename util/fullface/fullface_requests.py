import os, sys, requests, base64, shutil, datetime
import json, cv2
import argparse
import imutils


def getBase64(image):
    # lê imagem
    img = cv2.imread(image)
    # pega o formato
    height, width, channels = img.shape
    #verifica se altura é maior que largura para que o resize seja menor pela largura
    if height > width:
        img = imutils.resize(img, width=480)
    else:
        # verifica se largura é maior que altura
        img = imutils.resize(img, height=480)

    _, img_arr = cv2.imencode('.jpg', img)  # im_arr: image como Numpy one-dim array format.
    im_bytes = img_arr.tobytes()
    im_b64 = base64.b64encode(im_bytes).decode('utf-8')
    return im_b64

def image_resize(image, width = None, height = None, inter = cv2.INTER_AREA):
    # initialize the dimensions of the image to be resized and
    # grab the image size
    dim = None
    (h, w) = image.shape[:2]

    # if both the width and height are None, then return the
    # original image
    if width is None and height is None:
        return image

    # check to see if the width is None
    if width is None:
        # calculate the ratio of the height and construct the
        # dimensions
        r = height / float(h)
        dim = (int(w * r), height)

    # otherwise, the height is None
    else:
        # calculate the ratio of the width and construct the
        # dimensions
        r = width / float(w)
        dim = (width, int(h * r))

    # resize the image
    resized = cv2.resize(image, dim, interpolation = inter)

    # return the resized image
    return resized

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--cadastro", required=False,
	help="Faz o cadastro de uma face na Fullface")
ap.add_argument("-a", "--atualizar", required=False,
	help="show video window")
ap.add_argument("-r", "--record", required=False,
	help="save video output")
ap.add_argument("-f", "--fps", required=True,
	help="define FPS")
ap.add_argument("-rf", "--recon_faces", required=False,
	help="active face recognition")
args = vars(ap.parse_args())


imgBase64 = []
count = 0

url = "https://www.fullfacelab.com/fffacerecognition_NC/tokapi/token"

payload = 'username=API_Testes&password=fullfaceAPITeste&grant_type=password&scope=a94df8b7-90fd-49ac-9173-1f4da3782c6e'
headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
}
response = requests.request("POST", url, headers=headers, data=payload, verify=False)
access_token = response.json()['access_token']

start = datetime.datetime.now()
#for filename in os.listdir("../../recon/cropped"):
for filename in os.listdir("../../recon/to_create/nathalia/boas"):
    try:
        if filename.endswith(".jpg"):
            imgBase64.append(getBase64("../../recon/to_create/nathalia/boas/" + filename))
            #imgBase64.append(getBase64("../../recon/cropped/" + filename))
            #shutil.move("../../recon/done/" + filename, "../../recon/processed/")
            #count = count + 1
    except Exception:
        print("[E]" + str(sys.exc_info()))

url = "http://www.fullfacelab.com/fffacerecognition_NC/cadapi/users/register"

payload = json.dumps({
  "projectName": "a94df8b7-90fd-49ac-9173-1f4da3782c6e",
  "accessToken": access_token,
  "keys": [
    {
      "key": "nome",
      "value": "Nathália"
    },
    {
      "key": "genero",
      "value": "F"
    }
  ],
  "pictures": imgBase64
})
headers = {
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
end = datetime.datetime.now()
print(response.text)
print(str((end - start).total_seconds()))