#!/usr/bin/env python3


import requests

# Set the API endpoint
endpoint = 'https://api.tdameritrade.com/v1/marketdata/chains'

# Set your authorization headers
headers = {
    'Authorization': 'Bearer '
}

# Set the query parameters for the option chain request
params = {
    'symbol': 'NFLX',           # The stock symbol to retrieve the option chain for
    'contractType': 'PUT',      # The type of option contract to retrieve (CALL or PUT)
    'strikeCount': '20',        # The number of strikes above and below the ATM price
    'strategy': 'SINGLE',       # The option strategy (SINGLE, ANALYTICAL, COVERED, VERTICAL, CALENDAR, STRANGLE, STRADDLE, BUTTERFLY, CONDOR, DIAGONAL, COLLAR, ROLL)
    'range': 'OTM',             # The expiration range to include in the option chain (NTM for near-term options)
    'fromDate': '2023-05-12',   # The earliest expiration date to include in the option chain
    'toDate': '2023-05-19',     # The latest expiration date to include in the option chain
    'expMonth': '',             # The expiration month (e.g. JAN,FEB,MAR,...)
    'optionType': ''            # The type of option (STANDARD, MINI)
}

# Send the request and parse the response JSON
response = requests.get(endpoint, headers=headers, params=params)
if response.status_code == 200:
    option_chain = response.json()
    print(option_chain)
else:
    print('Error retrieving option chain:', response.status_code, response.reason)












