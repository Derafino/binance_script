import csv
import json
import os
import time
import sqlite3
import requests


class BinanceAPI:
    def __init__(self, api_key):
        self.api_key = api_key

    def fetch_data(self, symbol, interval):
        url = f"https://api.binance.com/api/v3/klines"
        headers = {
            'X-MBX-APIKEY': self.api_key
        }
        params = {
            'symbol': symbol, 'interval': interval
        }
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print("Error occurred while fetching data from the Binance API.")
            return None


def save_data_to_csv(data, symbol, interval):
    if data:
        filename = f"{symbol}_{interval}.csv"
        file_dir = os.path.dirname(os.path.abspath(__file__))
        data_folder = os.path.join(file_dir, "data")

        if not os.path.exists(data_folder):
            os.makedirs(data_folder)

        file_path = os.path.join(data_folder, filename)
        with open(file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(
                ["Kline open time",
                 "Open price",
                 "High price",
                 "Low price",
                 "Close price",
                 "Volume",
                 "Kline Close time",
                 "Quote asset volume",
                 "Number of trades",
                 "Taker buy base asset volume",
                 "Taker buy quote asset volume",
                 "Ignore"])

            for item in data:
                writer.writerow(item)

        print(f"Data for {symbol} ({interval}) saved in {filename} successfully.")


def save_data_to_database(data, symbol):
    if data:
        conn = sqlite3.connect('data/database.db')
        cursor = conn.cursor()

        cursor.execute('''CREATE TABLE IF NOT EXISTS binance_data (
                                    symbol TEXT,
                                    kline_open_time TEXT,
                                    open_price REAL,
                                    high_price REAL,
                                    low_price REAL,
                                    close_price REAL,
                                    volume REAL,
                                    kline_close_time TEXT,
                                    quote_asset_volume REAL,
                                    number_of_trades INTEGER,
                                    taker_buy_base_asset_volume REAL,
                                    taker_buy_quote_asset_volume REAL,
                                    ignore TEXT
                                  )''')

        for item in data:
            cursor.execute('''INSERT INTO binance_data VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                           (symbol,) + tuple(item))

        conn.commit()
        conn.close()
        print(f"Data for {symbol} saved in database successfully.")


def read_config(config_file):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, config_file)
    with open(config_path) as file:
        config = json.load(file)

    api_key = config['api_key']
    symbol = config['symbol']
    interval = config['interval']

    return api_key, symbol, interval


def perform_script(api_key, symbol, interval):
    binance = BinanceAPI(api_key)
    data = binance.fetch_data(symbol, interval)
    save_data_to_csv(data, symbol, interval)
    save_data_to_database(data, symbol)


def convert_interval(interval):
    numeric_value = int(interval[:-1])
    unit = interval[-1]

    if unit == "h":
        interval_seconds = numeric_value * 60 * 60
    elif unit == "d":
        interval_seconds = numeric_value * 60 * 60 * 24
    else:
        raise ValueError("Invalid interval unit.")
    return interval_seconds


def main():
    config_file = 'config.json'
    api_key, symbol, interval = read_config(config_file)
    interval_seconds = convert_interval(interval)
    try:
        while True:
            perform_script(api_key, symbol, interval)
            time.sleep(interval_seconds)
    except KeyboardInterrupt:
        print('Stopping...')


if __name__ == '__main__':
    main()
