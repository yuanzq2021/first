import requests
import time
from datetime import datetime, timedelta

BASE_URL = "https://fapi.binance.com"

def get_all_usdt_perpetual_futures():
    response = requests.get(f"{BASE_URL}/fapi/v1/exchangeInfo")
    data = response.json()
    return [
        a['symbol'] for a in data['symbols']
        if a['symbol'].endswith('USDT') 
        and a['status'] == 'TRADING'
        and a['contractType'] == 'PERPETUAL'
    ]

def get_price_change(symbol, start_time, end_time):
    params = {
        'pair': symbol,
        'contractType': 'PERPETUAL',
        'interval': '5m',
        'startTime': start_time,
        'endTime': end_time,
        'limit': 2
    }
    response = requests.get(f"{BASE_URL}/fapi/v1/continuousKlines", params=params)
    klines = response.json()
    
    if len(klines) < 2:
        return 0
    
    start_price = float(klines[0][4])
    end_price = float(klines[1][4])
    return (end_price - start_price) / start_price * 100

def get_top_5_changes(symbols):
    now = datetime.now()
    now = now - timedelta(minutes=now.minute % 5, seconds=now.second, microseconds=now.microsecond)
    end_time = int(now.timestamp() * 1000)
    start_time = int((now - timedelta(minutes=5)).timestamp() * 1000)

    changes = []
    for symbol in symbols:
        change = get_price_change(symbol, start_time, end_time)
        changes.append((symbol, change))

    changes.sort(key=lambda x: x[1], reverse=True)
    return changes[:5]

def main():
    symbols = get_all_usdt_perpetual_futures()
    
    while True:
        now = datetime.now()
        next_five_min = now + timedelta(minutes=5-now.minute%5) - timedelta(seconds=now.second, microseconds=now.microsecond)
        wait_seconds = (next_five_min - now).total_seconds()
        time.sleep(wait_seconds)

        top_5 = get_top_5_changes(symbols)
        print(f"Top 5 price changes in the last 5 minutes (as of {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}):")
        for symbol, change in top_5:
            print(f"{symbol}: {change:.2f}%")
        print("\n")

if __name__ == "__main__":
    main()
