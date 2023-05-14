#!/usr/bin/env python3

import os
import requests
import sqlite3
import time
from datetime import datetime, timezone, timedelta
import pytz
import json


with open('config.json') as f:
    config = json.load(f)

client_id = config['client_id']
refresh_token = config['refresh_token']

DB_NAME = 'tokens.db'


def create_database():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tokens
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, token TEXT, timestamp INTEGER)''')
    conn.commit()
    conn.close()


def insert_token(token):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    timestamp = int(datetime.now().timestamp())
    c.execute("INSERT INTO tokens (token, timestamp) VALUES (?, ?)", (token, timestamp))
    conn.commit()
    conn.close()


def get_latest_token():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT token FROM tokens ORDER BY timestamp DESC LIMIT 1")
    result = c.fetchone()
    conn.close()
    if result:
        return result[0]
    else:
        return None


def refresh_access_token(client_id, refresh_token):
    while True:
        url = "https://api.tdameritrade.com/v1/oauth2/token"

        payload = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": client_id
        }

        response = requests.post(url, data=payload)

        access_token = response.json()['access_token']

        insert_token(access_token)

        print(access_token)

        # check if it's past 4pm EST time on a weekday
        now = datetime.now(pytz.timezone('US/Eastern'))
        if now.weekday() < 5 and now.hour >= 16:
            break

        time.sleep(25 * 60)  # wait 25 minutes before requesting a new token

    return get_latest_token()


def get_access_token():
    if not os.path.isfile(DB_NAME):
        create_database()

    latest_token = get_latest_token()

    if not latest_token:
        latest_token = refresh_access_token(client_id, refresh_token)
        print(latest_token)
    else:
        print(latest_token)

    return latest_token



access_token = get_latest_token()

# Set the API endpoint
endpoint = 'https://api.tdameritrade.com/v1/marketdata/chains'

# Set your authorization headers
headers = {
    'Authorization': f'Bearer {access_token}'
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













