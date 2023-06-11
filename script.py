import csv

import os
import time
import sqlite3

from api import BinanceAPI
from config import api_key, symbol, interval

binance = BinanceAPI(api_key)


def save_data_to_csv(data):
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


def save_data_to_database(data):
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


def perform_script():
    data = binance.fetch_data(symbol, interval)
    save_data_to_csv(data)
    save_data_to_database(data)


def convert_interval():
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
    interval_seconds = convert_interval()
    try:
        while True:
            perform_script()
            time.sleep(interval_seconds)
    except KeyboardInterrupt:
        print('Stopping...')


if __name__ == '__main__':
    main()
