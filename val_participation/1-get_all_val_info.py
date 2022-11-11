# This file needs to be run in order to save the validator info (stake, operator address etc.) for all the active validators at the moment.

import os
import json
from dotenv import load_dotenv
import requests

# Load env variables
load_dotenv()
MAX_TXNS_PER_BLOCK = 50
RPC_URL = os.getenv('RPC_URL')
RPC_URL_3 = os.getenv('RPC_URL_3')
COSMOSCAN_API = os.getenv('COSMOSCAN_API')
headers = {'accept': 'application/json',}

ALL_VALS_LS = requests.get(RPC_URL_3+'/staking/validators', headers=headers).json()['result']
dir_path = os.path.dirname(os.path.realpath(__file__))+'/active_vals.json'
json.dump(ALL_VALS_LS, open(dir_path, 'w+'))