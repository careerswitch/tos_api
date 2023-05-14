#!/usr/bin/env python3

"""

use refresh_tokens()
to call function

"""

import getpass
import sqlite3
import time
import requests

def refresh_tokens():
    # Get user inputs
    client_id = getpass.getpass("Enter your TD Ameritrade client ID: ")
    refresh_token = getpass.getpass("Enter your TD Ameritrade refresh token: ")

    # Connect to the database
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

    while True:
        try:
            # Get the latest tokens from the database
            access_token, refresh_token = get_latest_tokens()
            if access_token is None or refresh_token is None:
                # If there are no existing tokens, request new ones
                url = "https://api.tdameritrade.com/v1/oauth2/token"
                payload = {
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                    "client_id": client_id
                }
                response = requests.post(url, data=payload)
                response.raise_for_status()
                tokens = response.json()
                access_token = tokens['access_token']
                refresh_token = tokens['refresh_token']
                # Store the new tokens in the database
                insert_tokens(access_token, refresh_token)
            else:
                # Use the refresh token to get a new access token
                url = "https://api.tdameritrade.com/v1/oauth2/token"
                payload = {
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                    "client_id": client_id
                }
                response = requests.post(url, data=payload)
                response.raise_for_status()
                tokens = response.json()
                access_token = tokens['access_token']
                # Update the access token in the database
                c.execute('UPDATE tokens SET access_token = ? WHERE refresh_token = ?', (access_token, refresh_token))
                conn.commit()
            print("Access token refreshed successfully")
        except Exception as e:
            print(f"An error occurred: {str(e)}")
        # Wait for 25 minutes before refreshing the tokens
        time.sleep(25 * 60)
        # Stop refreshing tokens and disconnect from database at close of market localtime
        if time.localtime().tm_hour >= 23:
            break

    # Close the database connection
    conn.close()

refresh_tokens()