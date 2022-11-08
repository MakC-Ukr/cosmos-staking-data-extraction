# This file is used to get the block signatures for a given range of block number. 
# Even though the `../single_validators.py` file is supposed to automatically save block signatures to `block_signatures/` folder, 
# this might be used JIC.

import requests
import json
import os
import base64
from dotenv import load_dotenv
import time

headers = {'accept': 'application/json'}
load_dotenv()
RPC_URL_3 = os.getenv('RPC_URL_3')

def get_signatures(_block_num):
    url = RPC_URL_3+f'/blocks/{_block_num}'
    block_info = requests.get(url, headers=headers).json()['block']['last_commit']['signatures']
    return block_info

START_BLOCK = 12763286
END_BLOCK = 12763590

for i in range(START_BLOCK, END_BLOCK+1):
    print(i)
    dir_path = os.path.dirname(os.path.realpath(__file__))+'/block_signatures/'+str(i)+'.json'
    signatures = get_signatures(i)
    json.dump(signatures, open(dir_path, 'w+'))
    time.sleep(0.5)
