#!/usr/bin/env python3

import requests
import sqlite3
import time

# Connect to database
conn = sqlite3.connect('tokens.db')
c = conn.cursor()

# Create table for tokens if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS tokens
             (access_token text, refresh_token text)''')

def insert_tokens(access_token, refresh_token):
    # Insert tokens into the database
    c.execute('INSERT INTO tokens VALUES (?, ?)', (access_token, refresh_token))
    conn.commit()

def get_latest_tokens():
    # Retrieve the latest tokens from the database
    c.execute('SELECT * FROM tokens ORDER BY ROWID DESC LIMIT 1')
    row = c.fetchone()
    if row is not None:
        access_token, refresh_token = row
        return access_token, refresh_token
    else:
        return None, None

def refresh_tokens():
    while True:
        # Get the latest tokens from the database
        access_token, refresh_token = get_latest_tokens()
        if access_token is None or refresh_token is None:
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
            # Store the new tokens in the database
            insert_tokens(access_token, refresh_token)
        # Use the access token to make an API call
        headers = {
            'Authorization': 'Bearer ' + access_token
        }
        response = requests.get('https://api.tdameritrade.com/v1/accounts', headers=headers)
        if response.status_code == 401:
            # If the access token has expired, use the refresh token to get a new access token
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
            # Update the tokens in the database
            insert_tokens(access_token, refresh_token)
            # Use the new access token to make an API call
            headers = {
                'Authorization': 'Bearer ' + access_token
            }
            response = requests.get('https://api.tdameritrade.com/v1/accounts', headers=headers)
        print(response.json())
        # Wait for 25 minutes before refreshing the tokens
        time.sleep(25 * 60)
        # Stop refreshing tokens and disconnect from database at 4 pm localtime
        if time.localtime().tm_hour >= 23:
            break

# Call the refresh_tokens() function to start refreshing the tokens
refresh_tokens()

# Close the database connection
conn.close()
