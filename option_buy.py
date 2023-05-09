import requests
import json
import datetime as dt

# Define parameters for API request
symbol = 'AAPL'  # Replace with your desired ticker symbol
option_type = 'PUT'
start_date = int((dt.datetime.now() - dt.timedelta(days=30)).timestamp() * 1000)
end_date = int(dt.datetime.now().timestamp() * 1000)
url = f'https://api.tdameritrade.com/v1/marketdata/chains?symbol={symbol}&contractType={option_type}&fromDate={start_date}&toDate={end_date}'

# Make API request and extract data
response = requests.get(url)
option_chain = response.json()
call_options = option_chain['callExpDateMap']
put_options = option_chain['putExpDateMap']

# Calculate previous day's high and current market price
today = dt.date.today()
one_day = dt.timedelta(days=1)
yesterday = today - one_day
yesterday_str = yesterday.strftime('%Y-%m-%d')
url = f'https://api.tdameritrade.com/v1/marketdata/{symbol}/pricehistory?periodType=day&period=2&frequencyType=daily'
response = requests.get(url)
history = response.json()['candles']
prev_high = max([candle['high'] for candle in history if candle['datetime'][:10] == yesterday_str])
curr_price = response.json()['lastPrice']

# Define options parameters
price_low = 0.75
price_high = 1.50
days_out_min = 7
days_out_max = 30
strike_offset = 3

# Find the put option with the lowest price within the specified parameters
selected_option = None
for date, options in put_options.items():
    exp_date = dt.datetime.strptime(date, '%m/%d/%Y')
    days_out = (exp_date - today).days
    if days_out_min <= days_out <= days_out_max:
        for strike, strikes in options.items():
            if curr_price - strike_offset - price_high <= float(strike) <= curr_price - strike_offset + price_high and price_low <= float(strikes[0]['bid']) <= price_high:
                if selected_option is None or float(strikes[0]['bid']) < float(selected_option['bid']):
                    selected_option = strikes[0]

# If an appropriate option is found, buy it
if selected_option:
    order = {
        "complexOrderStrategyType": "NONE",
        "orderType": "LIMIT",
        "session": "NORMAL",
        "price": str(round(float(selected_option['ask']), 2)),
        "duration": "GOOD_TILL_CANCEL",
        "orderStrategyType": "SINGLE",
        "orderLegCollection": [
            {
                "instruction": "BUY_TO_OPEN",
                "quantity": 1,
                "instrument": {
                    "symbol": selected_option['symbol'],
                    "assetType": "OPTION"
                }
            }
        ]
    }

    response = requests.post(f'https://api.tdameritrade.com/v1/accounts/<insert_your_account_id_here>/orders',
                             headers={'Authorization': 'Bearer <insert_your_access_token_here>',
                                      'Content-Type': 'application/json'},
                             data=json.dumps(order))
    print(response.text)
else:
    print('No appropriate options found')
