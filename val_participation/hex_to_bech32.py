# This code basically calls the SmartStake servers to get the mapping from hex to bech32 for the 175 validators
# It then writes the mapping to a file called bech32_to_hex.json
# Used for one-time use only

import json
import os
import pandas
import requests
import time

dir_path = os.path.dirname(os.path.realpath(__file__)) + "/active_vals.json"
all_addresses = [val["operator_address"] for val in json.load(open(dir_path))]
mapping = {}

for addr in all_addresses:
    url = f"https://7nkwv3z5t1.execute-api.us-east-1.amazonaws.com/prod/listData?type=getPool&frequencyHour=8H&frequencyDay=10D&address={addr}&key=2mwTEDr9zXJH323M&token=1667914073&app=ATOM"
    resp = requests.get(url).json()["val"]["hexAddress"]
    mapping[addr] = resp
    print(f"{addr} -> {resp}")
    time.sleep(4)

dir_path = os.path.dirname(os.path.realpath(__file__)) + "/bech32_to_hex.json"
print('Please type "save" to save the file')
# inp = input()
# if inp == 'save':
# json.dump(mapping, open(dir_path, 'w+'))
json.dump(mapping, open(dir_path, "w+"))
