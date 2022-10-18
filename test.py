import time
t = time.time()
import asyncio
import pandas as pd
import os
from dotenv import load_dotenv
import requests
from helpers import get_supply_bonded_ratio, get_n_validators, get_n_active_validators, get_fees_collected, get_activeValidators_and_time, get_validator_stake, get_precommit_ratio, headers, get_inflation, list_to_dict

# Parameters to set
TOTAL_ATTRIBUTES = 8 # must be equal to columns in table

# Loading prerequisites
load_dotenv()
df = pd.read_csv('data.csv')
df_ls = df.to_dict('records')
COLUMN_NAMES = list(df.columns)
RPC_URL = os.getenv('RPC_URL')
LATEST_BLOCK = requests.get(RPC_URL+'/cosmos/base/tendermint/v1beta1/blocks/latest', headers=headers).json()['block']['header']['height'] # gets latest block number
LATEST_BLOCK = int(LATEST_BLOCK) - 10
print("LATEST_BLOCK = ", LATEST_BLOCK)
VALIDATOR_ADDRESS= os.getenv('VALIDATOR_ADDRESS')

x = get_supply_bonded_ratio()[0]
x = get_inflation()
x = get_fees_collected(LATEST_BLOCK)
x = get_activeValidators_and_time(LATEST_BLOCK)[1]
x = get_precommit_ratio(LATEST_BLOCK)
x = get_validator_stake(VALIDATOR_ADDRESS)
x = get_supply_bonded_ratio()[1]
x = get_n_active_validators() # will mostly return 175

print("Time taken: ", time.time() - t)