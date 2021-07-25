import requests
import json

url = "http://www.fullfacelab.com/fffacerecognition_NC/autapi/users/authenticate"

payload = json.dumps({
  "projectName": "a94df8b7-90fd-49ac-9173-1f4da3782c6e",
  "accessToken": "tCZ9apo5fqRKNZMaiZbSxstJfBIL5syNpBIui-fZw99i9pZYfh6S4MYJ9_eXEwMy0qIdaMcyI5p_b0NwF92lSdSb6fkn1vIhWakhwgiwbAfgNcFGOd1YiuAIpccR7l3KN-oQiOY8eJyoxIIDmhY_AVHAuLSXqKqwBDPLOtNI95_lJDsa37N7awJBQ6hUTXL8",
  "keys": [],
  "pictures": [
    ""
  ]
})
headers = {
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
