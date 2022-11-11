import pandas as pd
import requests
import numpy as np
import json
import os
import base64
from dotenv import load_dotenv

headers = {'accept': 'application/json'}
load_dotenv()
VALIDATOR = 'cosmosvaloper1svwt2mr4x2mx0hcmty0mxsa4rmlfau4lwx2l69'

ALLTHATNODE_API_KEY = os.getenv('ALLTHATNODE_API_KEY')

def get_rewards(val_address, BLOCK):
    url = f'https://rpc.cosmos.network/block_results?height={BLOCK}'
    response = requests.get(url=url, headers=headers)
    begin_block_events = response.json()['result']['begin_block_events']
    for event in begin_block_events:
        if event['type'] == "rewards"  or event['type'] == "commission":
            if len(event['attributes']) != 2:
                # Probably skipping event with wrong shape
                pass
            else:
                a0 = event['attributes'][0]
                a1 = event['attributes'][1]
                try:
                    key0 = base64.b64decode(a0['key']).decode("utf-8")
                    value0 = base64.b64decode(a0['value']).decode("utf-8")
                    key1 = base64.b64decode(a1['key']).decode("utf-8")
                    value1 = base64.b64decode(a1['value']).decode("utf-8")
                    if key0 == "amount" and key1 == "validator" and value1 == val_address:
                        print(f"{value0} {event['type']} paid to our validator")
                except TypeError:
                    # Probably "argument should be a bytes-like object or ASCII string, not 'NoneType'"
                    # Probably missing key or value
                    pass

# url = f'https://rpc-cosmoshub.blockapsis.com/block_results?height=12763524'
# response = requests.get(url=url, headers=headers).json()
# json.dump(response, open('begin_block_events.json', 'w+'))
dir = json.load(fp=open('begin_block_events.json', 'r'))
x = [i['type'] for i in dir['result']['begin_block_events']]
print(pd.Series(x).unique())