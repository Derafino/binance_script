import requests
from config import cap_symbols


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

    @staticmethod
    def get_market_caps():
        url = 'https://api.binance.com/api/v3/ticker/24hr'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            market_caps = []
            data = [i for i in data if i['symbol'] in cap_symbols]
            for item in data:
                market_cap = float(item['quoteVolume']) * float(item['lastPrice'])
                market_caps.append((item['symbol'], market_cap))
            return market_caps
        else:
            return None
