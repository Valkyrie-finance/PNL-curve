import pandas as pd
import requests
from datetime import datetime
import time

# Load portfolio data
csv_path = 'portfolio_data.csv'
df = pd.read_csv(csv_path)

def fetch_btc_price(date_str):
    """Fetch BTC closing price for a given date (YYYY-MM-DD) from Binance API."""
    try:
        # Convert date to timestamp in milliseconds (Binance uses UTC)
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        start_ts = int(dt.timestamp()) * 1000
        end_ts = start_ts + 24 * 60 * 60 * 1000 - 1  # End of the day
        url = 'https://api.binance.com/api/v3/klines'
        params = {
            'symbol': 'BTCUSDT',
            'interval': '1d',
            'startTime': start_ts,
            'endTime': end_ts,
            'limit': 1
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data:
            close_price = float(data[0][4])
            return close_price
        else:
            return None
    except Exception as e:
        print(f"Error fetching BTC price for {date_str}: {e}")
        return None

# Prepare BTC price column
btc_prices = []
for idx, row in df.iterrows():
    date_str = str(row['Date'])[:10]
    if pd.isna(date_str) or len(date_str) < 10:
        btc_prices.append(None)
        continue
    price = fetch_btc_price(date_str)
    btc_prices.append(price)
    time.sleep(0.2)  # Be gentle to the API

df['BTC_Price'] = btc_prices

df.to_csv(csv_path, index=False)
print('BTC prices updated in portfolio_data.csv') 