import pandas as pd
import requests
from datetime import datetime, timedelta

# Load portfolio data
csv_path = 'portfolio_data.csv'
df = pd.read_csv(csv_path)

# Get all unique dates up to today
now = datetime.now().date()
dates = pd.to_datetime(df['Date'].astype(str).str[:10]).dt.date
valid_dates = sorted(set(d for d in dates if d <= now))

if valid_dates:
    start_ts = int(datetime.combine(valid_dates[0], datetime.min.time()).timestamp()) * 1000
    end_ts = int(datetime.combine(valid_dates[-1], datetime.min.time()).timestamp()) * 1000 + 24*60*60*1000
    url = 'https://api.binance.com/api/v3/klines'
    params = {
        'symbol': 'BTCUSDT',
        'interval': '1d',
        'startTime': start_ts,
        'endTime': end_ts,
        'limit': 1000  # Binance max is 1000, adjust if needed
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    # Print only the date and closing price for each candle
    print("Date and closing price for each candle:")
    for candle in data:
        ts = int(candle[0]) // 1000
        date_str = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d')
        close_price = candle[4]
        print(f"{date_str}: {close_price}")

    # Map Binance timestamps to close prices
    price_map = {}
    for candle in data:
        ts = int(candle[0]) // 1000
        date_str = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d')
        price_map[date_str] = float(candle[4])

    print(f"Number of candles returned: {len(data)}")
else:
    price_map = {}

# Assign prices to your DataFrame
btc_prices = []
last_price = None
for idx, row in df.iterrows():
    date_str = str(row['Date'])[:10]
    try:
        row_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except Exception:
        btc_prices.append(None)
        continue
    if row_date > now:
        btc_prices.append(None)
        continue
    price = price_map.get(date_str, None)
    if price is not None:
        last_price = price
        btc_prices.append(price)
    else:
        btc_prices.append(last_price)
    print(f"Row {idx+1}/{len(df)}: {date_str} -> {btc_prices[-1]}")

df['BTC_Price'] = btc_prices

df.to_csv(csv_path, index=False)
print('BTC prices updated in portfolio_data.csv') 