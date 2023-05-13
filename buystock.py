#!/usr/bin/env python3

import requests

access_token = ""
account_id = ""

url = f"https://api.tdameritrade.com/v1/accounts/{account_number}/orders"

headers = {
    "Authorization": f"Bearer {access_token}"
}

payload = {
    "orderType": "MARKET",
    "session": "NORMAL",
    "duration": "DAY",
    "orderStrategyType": "SINGLE",
    "orderLegCollection": [{
        "instruction": "BUY",
        "quantity": 100,
        "instrument": {
            "symbol": "AAPL",
            "assetType": "EQUITY"
        }
    }]
}

response = requests.post(url, headers=headers, json=payload)

if response.status_code == 200:
    data = response.json()
    print(data)
elif response.status_code == 400:
    data = response.json()
    print(f"Error: {response.status_code} - {data['error'][0]['error']}")
else:
    print(f"Error: {response.status_code} - {response.text}")