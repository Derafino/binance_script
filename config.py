import json
import os

config_file = 'config.json'

script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, config_file)
with open(config_path) as file:
    config = json.load(file)

api_key = config['api_key']
symbol = config['symbol']
interval = config['interval']
cap_symbols = config['cap_symbols']


