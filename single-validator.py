import time
import threading
import pandas as pd
import os
from threading import Thread
from time import sleep
from dotenv import load_dotenv
import requests
from helpers import bcolors, get_rewards, get_block_time, get_total_supply, get_chain_distribution_parameters, get_supply_bonded_ratio, get_n_validators, get_n_active_validators, get_total_fees, get_timestamp, get_validator_stake, get_precommit_ratio, headers, get_inflation, list_to_dict, get_validator_commission

# Loading prerequisites
load_dotenv()
VALIDATOR_NAME = "Twinstake"
dir_path = dir_path = os.path.dirname(os.path.realpath(__file__))+ f'/single-validators/{VALIDATOR_NAME}.csv'
df = pd.read_csv(dir_path)
df_ls = df.to_dict('records')
COLUMN_NAMES = list(df.columns)
RPC_URL = os.getenv('RPC_URL')
VALIDATOR_ADDRESS= "cosmosvaloper1svwt2mr4x2mx0hcmty0mxsa4rmlfau4lwx2l69"
N_ACTIVE_VALIDATORS = int(requests.get(RPC_URL+'/validatorsets/latest', headers=headers).json()['result']['total'])
print("Loaded libraries...")

# CONST VALUES - 9,10,11,12,13,17,21
BLOCKS_PRE_YEAR = 4360000
CONST_ATTRIBUTES = {
        "Block_length_target": (365*24*60*60)/BLOCKS_PRE_YEAR,
        "Goal_Bonded": 0.6666,
        "Inflation_Rate_Change": 0.13,
        "Min_Inflation_Rate": 0.07,
        "Max_Inflation_Rate": 0.20,
        "Min_Signatures": 0.6666,
        "Blocks_per_year": BLOCKS_PRE_YEAR,
        "Validator_id": VALIDATOR_ADDRESS
    }


# No API calls to get data
def MyThread0(res, _latest_block):
    # t = time.time()
    res['block_num'] = _latest_block
    for key in CONST_ATTRIBUTES.keys():
        res[key] = CONST_ATTRIBUTES[key]
    # print(time.time()-t, "s for thread 0")

# 1 - INFLATION RATE
def MyThread1(res, key):
    t = time.time()
    res[key] = get_inflation() 
    print(time.time()-t, "s for thread 1")

# 0 - PERCENTAGE ATOM STAKED
def MyThread2(res, key):
    t = time.time()
    res[key] = get_supply_bonded_ratio()
    print(time.time()-t, "s for thread 2")

# 2, 20 - Total_Fees_Per_Block and txFees
def MyThread3(res, key, _latest_block):
    t = time.time()
    res[key] = get_total_fees(_latest_block)
    res[key] = 14916
    print(time.time()-t, "s for thread 3")

# 4 - block timestamp
# def MyThread4(res, key, _latest_block):
#     res[key] = get_timestamp(_latest_block)
def MyThread4(res, key, _timestamp):
    # t = time.time()
    res[key] = _timestamp
    # print(time.time()-t, "s for thread 4")

# 5 - PRECOMMITS RATIO
def MyThread5(res, key, num_signatures):
    # t = time.time()
    res[key] = int(num_signatures)/N_ACTIVE_VALIDATORS
    # print(time.time()-t, "s for thread 5")

# 6 - ATOM STAKED BY VALIDATOR
def MyThread6(res, key):
    t = time.time()
    res[key] = get_validator_stake(VALIDATOR_ADDRESS)
    print(time.time()-t, "s for thread 6")

# 7 - TOTAL SUPPLY - THIS IS WRONG
def MyThread7(res, key):
    t = time.time()
    res[key] = get_total_supply()
    print(time.time()-t, "s for thread7")

# 8 - N ACTIVE VALIDATORS
def MyThread8(res, key):
    t = time.time()
    N_ACTIVE_VALIDATORS = get_n_active_validators()
    res[key] = N_ACTIVE_VALIDATORS
    print(time.time()-t, "s for thread 8")

# 14, 15, 16 - min proposer bonus, max proposer bonus, community tax
def MyThread9(res):
    t = time.time()
    result_dict = get_chain_distribution_parameters()
    for key in result_dict.keys():
        res[key] = result_dict[key]
    print(time.time()-t, "s for thread 9")

# 18 - Rewards
def MyThread10(res, validator_addr):
    t = time.time()
    result_dict = get_rewards(validator_addr)
    for key in result_dict.keys():
        res[key] = result_dict[key]
    print(time.time()-t, "s for thread 10")

# 22 - validator commission
def MyThread11(res, key, validator_addr):
    t = time.time()
    res[key] = get_validator_commission(validator_addr)
    print(time.time()-t, "s for thread 11")

def get_all_block_data(LATEST_BLOCK, num_signatures, _timestamp):
    result = {}

    all_threads = [
        threading.Thread(target=MyThread0, args=[result, LATEST_BLOCK]),
        threading.Thread(target=MyThread1, args=[result, "inflation_rate"]),
        threading.Thread(target=MyThread2, args=[result, "percent_staked"]),
        threading.Thread(target=MyThread3, args=[result, "total_block_fees", LATEST_BLOCK]),
        threading.Thread(target=MyThread4, args=[result, "timestamp", _timestamp]),
        threading.Thread(target=MyThread5, args=[result, "sign_ratio", num_signatures]),
        threading.Thread(target=MyThread6, args=[result, "atom_staked_v"]),
        threading.Thread(target=MyThread7, args=[result, "total_supply"]),
        threading.Thread(target=MyThread8, args=[result, "n_validators"]),
        threading.Thread(target=MyThread9, args=[result]),
        threading.Thread(target=MyThread10, args=[result, VALIDATOR_ADDRESS]),
        threading.Thread(target=MyThread11, args=[result, "v_commission", VALIDATOR_ADDRESS])
    ]

    t = time.time()
    for thread in all_threads:
        thread.start()

    for thread in all_threads:
        thread.join()

    df_ls.append(result)
    pd.DataFrame(df_ls).to_csv(dir_path, index=False)

    print(bcolors.OKCYAN, "Time taken for block : ", LATEST_BLOCK, ": ", time.time() - t, bcolors.ENDC)
    print()

past_block_num = 0
new_block = 0
num_signatures = 0
time_stamp = 0
while(True):
    while past_block_num == new_block:
        resp = requests.get(RPC_URL+'/cosmos/base/tendermint/v1beta1/blocks/latest', headers=headers).json() # gets latest block number
        new_block = int(resp['block']['header']['height'])
        print(new_block)
        num_signatures=len(resp['block']['last_commit']['signatures'])
        time_stamp = resp['block']['header']['time']
    print(bcolors.OKCYAN, "BLOCK ", new_block, bcolors.ENDC)
    get_all_block_data(new_block, num_signatures, time_stamp)
    past_block_num = new_block