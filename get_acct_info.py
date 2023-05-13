#!/usr/bin/env python3

import requests

access_token = ""

url = "https://api.tdameritrade.com/v1/accounts"

headers = {
    "Authorization": f"Bearer {access_token}"
}

response = requests.get(url, headers=headers)

print(response.json())
