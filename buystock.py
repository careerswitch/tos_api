#!/usr/bin/env python3

import requests
import json
import get_token


# Load the credentials from config.json
with open('config.json') as f:
    credentials = json.load(f)

# Extract the required values from the credentials
ACCOUNT_NUMBER = credentials['account_number']


url = f"https://api.tdameritrade.com/v1/accounts/{ACCOUNT_NUMBER}/orders"

headers = {
    "Authorization": f"Bearer {get_token.get_latest_token()}"
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