#!/usr/bin/env python3

import requests
import sqlite3
import time
import datetime

# Connect to database
conn = sqlite3.connect('tokens.db')
c = conn.cursor()

# Create table for tokens if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS tokens
             (access_token text, refresh_token text, expiry_time text)''')

# Insert tokens into the database
def insert_tokens(access_token, refresh_token, expiry_time):
    c.execute('INSERT INTO tokens VALUES (?, ?, ?)', (access_token, refresh_token, expiry_time))
    conn.commit()

# Get latest tokens from the database
def get_latest_tokens():
    c.execute('SELECT * FROM tokens ORDER BY ROWID DESC LIMIT 1')
    row = c.fetchone()
    if row is not None:
        access_token, refresh_token, expiry_time = row
        return access_token, refresh_token, datetime.datetime.fromisoformat(expiry_time)
    else:
        return None

# Refresh tokens if they have expired
def refresh_tokens():
    latest_tokens = get_latest_tokens()
    if latest_tokens is None:
        # If there are no existing tokens, request new ones
        url = "https://api.tdameritrade.com/v1/oauth2/token"
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": "<YOUR_REFRESH_TOKEN>",
            "client_id": "<YOUR_CLIENT_ID>"
        }
        response = requests.post(url, data=payload)
        response.raise_for_status()
        tokens = response.json()
        access_token = tokens['access_token']
        refresh_token = tokens['refresh_token']
        expiry_time = datetime.datetime.now() + datetime.timedelta(seconds=tokens['expires_in'])
        insert_tokens(access_token, refresh_token, expiry_time.isoformat())
        return access_token
    else:
        access_token, refresh_token, expiry_time = latest_tokens
        if datetime.datetime.now() < expiry_time:
            # If the access token is still valid, use it
            return access_token
        else:
            # If the access token has expired, use the refresh token to get a new one
            url = "https://api.tdameritrade.com/v1/oauth2/token"
            payload = {
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": "<YOUR_CLIENT_ID>"
            }
            response = requests.post(url, data=payload)
            response.raise_for_status()
            tokens = response.json()
            access_token = tokens['access_token']
            refresh_token = tokens['refresh_token']
            expiry_time = datetime.datetime.now() + datetime.timedelta(seconds=tokens['expires_in'])
            insert_tokens(access_token, refresh_token, expiry_time.isoformat())
            return access_token

# Run the code until 4pm
while datetime.datetime.now().time() < datetime.time(hour=16):
    access_token = refresh_tokens()
    # Use the access token to make an API call
    headers = {
        'Authorization': 'Bearer ' + access_token
    }
    response = requests.get('https://api.tdameritrade.com/v1/accounts', headers=headers)
    print(response.json())
    # Wait for 25 minutes before refreshing tokens and making another API call
    time.sleep(25 * 60)

# Close the database connection
conn.close()
