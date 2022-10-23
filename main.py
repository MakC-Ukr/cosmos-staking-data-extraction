import time
import threading
import pandas as pd
import os
from threading import Thread
from time import sleep
from dotenv import load_dotenv
import requests
from helpers import bcolors, get_rewards, get_chain_distribution_parameters, get_supply_bonded_ratio, get_n_validators, get_n_active_validators, get_fees_collected, get_timestamp, get_validator_stake, get_precommit_ratio, headers, get_inflation, list_to_dict

# Loading prerequisites
load_dotenv()
df = pd.read_csv('data.csv')
df_ls = df.to_dict('records')
COLUMN_NAMES = list(df.columns)
RPC_URL = os.getenv('RPC_URL')
VALIDATOR_ADDRESS= os.getenv('VALIDATOR_ADDRESS')

# CONST VALUES - 9,10,11,12,13,17,21
CONST_ATTRIBUTES = {
        "Block_length_target": -1,
        "Goal_Bonded": 0.6666,
        "Inflation_Rate_Change": 0.13,
        "Min_Inflation_Rate": 0.07,
        "Max_Inflation_Rate": 0.20,
        "Min_Signatures": 0.6666,
        "Blocks_per_year": -1,
        "Validator_id": VALIDATOR_ADDRESS
    }


# 0 - No API calls to get data
def MyThread0(res, _latest_block):
    res['block_num'] = _latest_block
    for key in CONST_ATTRIBUTES.keys():
        res[key] = CONST_ATTRIBUTES[key]


# 1 - INFLATION RATE
def MyThread1(res, key):
    res[key] = get_inflation() 

# 2 - PERCENTAGE ATOM STAKED
def MyThread2(res, key):
    res[key] = get_supply_bonded_ratio()

# 3, 20 - BLOCK FEES and txFees
def MyThread3(res, key, _latest_block):
    res[key] = get_fees_collected(_latest_block)

# 4 - BLOCK LENGTH
def MyThread4(res, key, _latest_block):
    res[key] = get_timestamp(_latest_block)

# 5 - PRECOMMITS RATIO
def MyThread5(res, key, _latest_block):
    res[key] = get_precommit_ratio(_latest_block)

# 6 - ATOM STAKED BY VALIDATOR
def MyThread6(res, key):
    res[key] = get_validator_stake(VALIDATOR_ADDRESS)

# 7 - TOTAL SUPPLY - THIS IS WRONG
def MyThread7(res, key):
    res[key] = get_supply_bonded_ratio()

# 8 - N ACTIVE VALIDATORS
def MyThread8(res, key):
    res[key] = get_n_active_validators() 

# 14, 15, 16 - min proposer bonus, max proposer bonus, community tax
def MyThread9(res):
    result_dict = get_chain_distribution_parameters()
    for key in result_dict.keys():
        res[key] = result_dict[key]


def MyThread10(res, validator_addr):
    result_dict = get_rewards(validator_addr)
    for key in result_dict.keys():
        res[key] = result_dict[key]

def get_all_block_data(LATEST_BLOCK):
    result = {}

    all_threads = [
        threading.Thread(target=MyThread0, args=[result, LATEST_BLOCK]),
        threading.Thread(target=MyThread1, args=[result, "inflation_rate"]),
        threading.Thread(target=MyThread2, args=[result, "percent_staked"]),
        threading.Thread(target=MyThread3, args=[result, "total_block_fees", LATEST_BLOCK]),
        threading.Thread(target=MyThread4, args=[result, "block_len", LATEST_BLOCK]),
        threading.Thread(target=MyThread5, args=[result, "sign_ratio", LATEST_BLOCK]),
        threading.Thread(target=MyThread6, args=[result, "atom_staked_v"]),
        threading.Thread(target=MyThread7, args=[result, "total_supply"]),
        threading.Thread(target=MyThread8, args=[result, "n_validators"]),
        threading.Thread(target=MyThread9, args=[result]),
        threading.Thread(target=MyThread10, args=[result, VALIDATOR_ADDRESS])
    ]

    t = time.time()
    for thread in all_threads:
        thread.start()

    for thread in all_threads:
        thread.join()

    df_ls.append(result)
    pd.DataFrame(df_ls).to_csv('data.csv', index=False)

    print(bcolors.OKCYAN, "Time taken for block : ", LATEST_BLOCK, ": ", time.time() - t, bcolors.ENDC)
    print()

while(True):
    past_block_num = 0
    new_block = 0
    while past_block_num == new_block:
        time.sleep(2)
        new_block = int(requests.get(RPC_URL+'/cosmos/base/tendermint/v1beta1/blocks/latest', headers=headers).json()['block']['header']['height']) # gets latest block number

    print(bcolors.OKCYAN, "BLOCK ", new_block, bcolors.ENDC)
    get_all_block_data(new_block)
    past_block_num = new_block