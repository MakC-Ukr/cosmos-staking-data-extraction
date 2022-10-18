import time
t = time.time()
import threading
import pandas as pd
import os
from threading import Thread
from time import sleep
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

result = {}

# block_num, inflation_rate, percent_staked, total_block_fees, block_len, sign_ratio, atom_staked_v, total_supply, n_validators


# 0 - BLOCK NUMBER
def get_block_num():
    return LATEST_BLOCK
def MyThread0(res, key):
    res[key] = get_block_num()

# 1 - INFLATION RATE
def MyThread1(res, key):
    res[key] = get_inflation() # get_inflation imported directly from helpers

# 2 - PERCENTAGE ATOM STAKED
def get_percent_staked():
    return get_supply_bonded_ratio()[1]
def MyThread2(res, key):
    res[key] = get_percent_staked()

# 3 - BLOCK FEES
def get_total_block_fees():
    return get_fees_collected(LATEST_BLOCK)
def MyThread3(res, key):
    res[key] = get_total_block_fees()

# 4 - BLOCK LENGTH
def get_block_len():
    return get_activeValidators_and_time(LATEST_BLOCK)[1]
def MyThread4(res, key):
    res[key] = get_block_len()

# 5 - PRECOMMITS RATIO
def get_sign_ratio():
    get_precommit_ratio(LATEST_BLOCK)
def MyThread5(res, key):
    res[key] = get_block_len()

# 6 - ATOM STAKED BY VALIDATOR
def get_atom_staked_v():
    return get_validator_stake(VALIDATOR_ADDRESS)
def MyThread6(res, key):
    res[key] = get_atom_staked_v()

# 7 - TOTAL SUPPLY
def get_total_supply():
    return get_supply_bonded_ratio()[0]
def MyThread7(res, key):
    res[key] = get_total_supply()

# 8 - N ACTIVE VALIDATORS
def MyThread8(res, key):
    res[key] = get_n_active_validators() # imported directly from helpers

all_threads = [
    threading.Thread(target=MyThread0, args=[result, "block_num"]),
    threading.Thread(target=MyThread1, args=[result, "inflation_rate"]),
    threading.Thread(target=MyThread2, args=[result, "percent_staked"]),
    threading.Thread(target=MyThread3, args=[result, "total_block_fees"]),
    threading.Thread(target=MyThread4, args=[result, "block_len"]),
    threading.Thread(target=MyThread5, args=[result, "sign_ratio"]),
    threading.Thread(target=MyThread6, args=[result, "atom_staked_v"]),
    threading.Thread(target=MyThread7, args=[result, "total_supply"]),
    threading.Thread(target=MyThread8, args=[result, "n_validators"])
]

for thread in all_threads:
    thread.start()

for thread in all_threads:
    thread.join()

df_ls.append(result)
pd.DataFrame(df_ls).to_csv('data.csv', index=False)

print("Time taken: ", time.time() - t)