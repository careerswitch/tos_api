#!/usr/bin/env python3

import json
import os
import sqlite3
import time
from datetime import datetime, timedelta
import requests

db_name = 'tokens.db'


def create_database():
    print("Creating tokens database...")
    try:
        conn = sqlite3.connect(db_name, check_same_thread=False)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS tokens
                     (timestamp INTEGER PRIMARY KEY AUTOINCREMENT, token TEXT)''')
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"Error creating database: {e}")
        return None


def insert_token(token):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    timestamp = int(datetime.now().timestamp())
    c.execute("INSERT INTO tokens (token, timestamp) VALUES (?, ?)", (token, timestamp))
    conn.commit()
    conn.close()

    # Format the timestamp as a string
    time_str = datetime.fromtimestamp(timestamp).strftime("%m-%d-%Y %I:%M %p")

    print(f"New token created at {time_str}")


def get_latest_token():
    conn = sqlite3.connect(db_name)
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
        access_token = response.json().get('access_token')

        if access_token:
            insert_token(access_token)
            print("Access token retrieved and inserted into the database")
        else:
            print("Failed to retrieve access token from the API")

        time.sleep(25 * 60)  # wait 25 minutes before requesting a new token
        delete_old_tokens()  # delete any old tokens before getting the latest token

    return access_token


def delete_old_tokens():
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    timestamp_threshold = int((datetime.now() - timedelta(minutes=25)).timestamp())
    c.execute("DELETE FROM tokens WHERE timestamp < ?", (timestamp_threshold,))
    conn.commit()
    conn.close()


def main():
    if not os.path.isfile(db_name):
        create_database()

    while True:
        latest_token = get_latest_token()

        if not latest_token:
            print("No latest token found in the database.")
            with open('config.json') as f:
                config = json.load(f)

            client_id = config.get('client_id')
            refresh_token = config.get('refresh_token')

            if client_id and refresh_token:
                delete_old_tokens()  # delete any old tokens before getting the latest token
                latest_token = refresh_access_token(client_id, refresh_token)
            else:
                print("Invalid client_id or refresh_token in config.json")

        else:
            print("Latest token retrieved from the database:", latest_token[:5])

        time.sleep(25 * 60)  # wait 25 minutes before requesting a new token and deleting old tokens
        delete_old_tokens()  # delete any old tokens after 25 minutes have passed


if __name__ == '__main__':
    main()

# !/usr/bin/env python3

# import json
# import os
# import sqlite3
# import time
# from datetime import datetime, timedelta
# import requests
#
# db_name = 'tokens.db'
#
#
# def create_database():
#     print("Creating tokens database...")
#     try:
#         conn = sqlite3.connect(db_name, check_same_thread=False)
#         c = conn.cursor()
#         c.execute('''CREATE TABLE IF NOT EXISTS tokens
#                      (timestamp INTEGER PRIMARY KEY AUTOINCREMENT, token TEXT)''')
#         conn.commit()
#         conn.close()
#     except sqlite3.Error as e:
#         print(f"Error creating database: {e}")
#         return None
#
#
# def insert_token(token):
#     conn = sqlite3.connect(db_name)
#     c = conn.cursor()
#     timestamp = int(datetime.now().timestamp())
#     c.execute("INSERT INTO tokens (token, timestamp) VALUES (?, ?)", (token, timestamp))
#     conn.commit()
#     conn.close()
#
#     # Format the timestamp as a string
#     time_str = datetime.fromtimestamp(timestamp).strftime("%m-%d-%Y %I:%M %p")
#
#     print(f"New token created at {time_str}")
#
#
# def get_latest_token():
#     conn = sqlite3.connect(db_name)
#     c = conn.cursor()
#     c.execute("SELECT token FROM tokens ORDER BY timestamp DESC LIMIT 1")
#     result = c.fetchone()
#     conn.close()
#
# #    print("Check database for result of get_latest_token()")
#
#     if result:
#         return result[0]
#     else:
#         return None
#
#
# def refresh_access_token(client_id, refresh_token):
#     while True:
#         url = "https://api.tdameritrade.com/v1/oauth2/token"
#
#         payload = {
#             "grant_type": "refresh_token",
#             "refresh_token": refresh_token,
#             "client_id": client_id
#         }
#
#         response = requests.post(url, data=payload)
#         access_token = response.json()['access_token']
#
#         insert_token(access_token)
#
#         time.sleep(25 * 60)  # wait 25 minutes before requesting a new token
#         delete_old_tokens()  # delete any old tokens before getting the latest token
#
#     return access_token
#
#
# def delete_old_tokens():
#     conn = sqlite3.connect(db_name)
#     c = conn.cursor()
#     timestamp_threshold = int((datetime.now() - timedelta(minutes=25)).timestamp())
#     c.execute("DELETE FROM tokens WHERE timestamp < ?", (timestamp_threshold,))
#     conn.commit()
#     conn.close()
#
#
# def main():
#     if not os.path.isfile(db_name):
#         create_database()
#
#     while True:
#         latest_token = get_latest_token()
#
#         if not latest_token:
#             print("No latest token found in the database.")
#             with open('config.json') as f:
#                 config = json.load(f)
#
#             client_id = config['client_id']
#             refresh_token = config['refresh_token']
#
#             delete_old_tokens()  # delete any old tokens before getting the latest token
#             latest_token = refresh_access_token(client_id, refresh_token)
#
#         else:
#             print("Check database for latest token:", latest_token[:5])
#
#
#         time.sleep(25 * 60)  # wait 25 minutes before requesting a new token and deleting old tokens
#         delete_old_tokens()  # delete any old tokens after 25 minutes have passed
#
#
# if __name__ == '__main__':
#     main()
