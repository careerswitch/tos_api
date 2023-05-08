#!/usr/bin/env python3


import tdameritrade.auth as td_auth
import tdameritrade.client as td_client
import datetime as dt

# Enter your TD Ameritrade account credentials
CLIENT_ID = 'your_client_id'
REDIRECT_URI = 'your_redirect_uri'
ACCOUNT_NUMBER = 'your_account_number'
CREDENTIALS_PATH = 'path_to_your_credentials_file'

# Authenticate and create a client object
TDSession = td_auth.TDAuth(CLIENT_ID, REDIRECT_URI, CREDENTIALS_PATH)
TDSession.login()
TDClient = td_client.TDClient(TDSession)

# Define the symbol and date range
symbol = 'AAPL'
end_date = dt.datetime.today()
start_date = end_date - dt.timedelta(days=1)

# Get the historical prices
hist_price = TDClient.get_price_history(symbol=symbol, period_type='day',
                                        start_date=start_date, end_date=end_date,
                                        frequency_type='minute', frequency=1)

# Get the previous day's high price
prev_high = max(hist_price['high'])

# Get the current market price
cur_price = hist_price['close'][-1]

# Define the range of strike prices to check
strike_range = range(int(cur_price - 3), int(prev_high), -1)

# Loop over each strike price in the range
for strike_price in strike_range:

    # Define the expiration date (7 days out)
    exp_date = (end_date + dt.timedelta(days=7)).strftime('%Y-%m-%d')

    # Download the option chain for the put options with the given strike price and expiration date
    option_chain = TDClient.get_options_chain(symbol=symbol, contract_type='PUT',
                                              strike=strike_price, from_date=exp_date,
                                              to_date=exp_date, include_quotes=True)

    # Filter the option chain to include only options with prices between $1.00 and $1.50
    filtered_chain = [option for option in option_chain['putExpDateMap'][exp_date][str(strike_price)]
                      if 1.0 <= option['last'] <= 1.5]

    # If at least one option meets the criteria, buy the first option in the list
    if len(filtered_chain) > 0:
        option = filtered_chain[0]
        option_symbol = option['symbol']
        quantity = 1
        order_price = option['ask']
        order = TDClient.place_order(ACCOUNT_NUMBER, 'AAPL', quantity, 'BUY_TO_OPEN', 'LIMIT', 'GTC',
                                     price=order_price,
                                     order_strategy_type='SINGLE',
                                     order_leg_collection=[{'instruction': 'BUY_TO_OPEN',
                                                            'quantity': quantity,
                                                            'instrument': {'symbol': option_symbol,
                                                                           'assetType': 'OPTION'}
                                                            }]
                                     )
        print(f"Bought 1 {option_symbol} put option at {order_price}")
        break
