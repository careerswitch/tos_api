"""
template for retrieving access_token TD API

import requests

url = "https://api.tdameritrade.com/v1/oauth2/token"

payload = {
    "grant_type": "refresh_token",
    "refresh_token": "<Your Refresh Token>",
    "client_id": "<Your API Key>"
}

response = requests.post(url, data=payload)

access_token = response.json()['access_token']

print(access_token)
"""


import requests

url = "https://api.tdameritrade.com/v1/oauth2/token"

payload = {
    "grant_type": "refresh_token",
    "refresh_token": "",
    "client_id": ""
}

response = requests.post(url, data=payload)

access_token = response.json()['access_token']

print(access_token)

