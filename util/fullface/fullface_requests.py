import os, sys, requests, base64, shutil, datetime
import json


def getBase64(image):
    with open(image, "rb") as img_file:
        img64 = base64.b64encode(img_file.read()).decode('utf-8')
    return img64

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
for filename in os.listdir("../../recon/to_create/nathalia"):
    try:
        if filename.endswith(".jpg"):
            imgBase64.append(getBase64("../../recon/to_create/nathalia" + filename))
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

response.json()


response = requests.request("POST", url, headers=headers, data=payload, verify=False)
end = datetime.datetime.now()
print(response.text)
print(str((end - start).total_seconds()))