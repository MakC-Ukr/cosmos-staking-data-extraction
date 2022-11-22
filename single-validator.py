import time
from tqdm import tqdm
import threading
import json
import os
import pandas as pd
from threading import Thread
from dotenv import load_dotenv
from time import sleep
from datetime import datetime
import requests
from helpers import bcolors, get_signatures, post_process_data, get_sign_ratio_from_signatures_array, get_rewards_current, get_block_time, get_total_supply, get_chain_distribution_parameters, get_supply_bonded_ratio, get_n_validators, get_n_active_validators, get_total_fees, get_timestamp, get_validator_stake, get_precommit_ratio, headers, get_inflation, list_to_dict, get_validator_commission

# parameters to set
load_dotenv()
N_BLOCKS_TO_GET = 150
VALIDATOR_NAME = ["Coinbase", "Twinstake", "Figment"]
VALIDATOR_ADDRESS = ["cosmosvaloper1c4k24jzduc365kywrsvf5ujz4ya6mwympnc4en", "cosmosvaloper1svwt2mr4x2mx0hcmty0mxsa4rmlfau4lwx2l69", "cosmosvaloper1hjct6q7npsspsg3dgvzk3sdf89spmlpfdn6m9d"]
datafile_name = "multiple"

# Loading prerequisites
VALIDATOR_STAKES = []
assert len(VALIDATOR_ADDRESS) == len(VALIDATOR_NAME), "VALIDATOR_ADDRESS and VALIDATOR_NAME must have the same length"
for i in range(len(VALIDATOR_ADDRESS)):
    VALIDATOR_STAKES.append(get_validator_stake(VALIDATOR_ADDRESS[i]))

RPC_URL = os.getenv('RPC_URL')
RPC_URL_PRIVATE = os.getenv('RPC_URL_PRIVATE')
N_ACTIVE_VALIDATORS = int(requests.get(RPC_URL+'/validatorsets/latest', headers=headers).json()['result']['total'])
CHAIN_DISTRIBUTION_PARAMS = get_chain_distribution_parameters()

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
        "n_validators": N_ACTIVE_VALIDATORS
    }

for i in range(len(VALIDATOR_ADDRESS)):
    CONST_ATTRIBUTES[f'val_{i}_name'] = VALIDATOR_NAME[i]
    CONST_ATTRIBUTES[f'val_{i}_address'] = VALIDATOR_ADDRESS[i]
    CONST_ATTRIBUTES[f'val_{i}_commission_pct'] = get_validator_commission(VALIDATOR_ADDRESS[i])


print(CONST_ATTRIBUTES)

# No API calls to get data
def MyThread0(res, _latest_block):
    t = time.time()
    res['block_num'] = _latest_block
    for key in CONST_ATTRIBUTES.keys():
        res[key] = CONST_ATTRIBUTES[key]
    print(time.time()-t, "s for thread 0")

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
    # res[key] = get_total_fees(_latest_block)
    res[key] = 0
    print(time.time()-t, "s for thread 3")

# 4 - block timestamp and proposer address
def MyThread4(res, key, _data):
    t = time.time()
    res[key] = _data
    print(time.time()-t, "s for thread 4")

# 5 - PRECOMMITS RATIO
def MyThread5(res, key, _block_signatures):
    t = time.time()
    res[key] = get_sign_ratio_from_signatures_array(_block_signatures, N_ACTIVE_VALIDATORS)
    print(time.time()-t, "s for thread 5")

# 6 - ATOM STAKED BY VALIDATOR
def MyThread6(res, key):
    t = time.time()
    for i in range(len(VALIDATOR_ADDRESS)):
        res[f'val_{i}_stake'] = VALIDATOR_STAKES[i]
    print(time.time()-t, "s for thread 6")

# 7 - TOTAL SUPPLY 
def MyThread7(res, key):
    t = time.time()
    res[key] = get_total_supply()
    print(time.time()-t, "s for thread7")

# 8 - N ACTIVE VALIDATORS
def MyThread8(res, key):
    t = time.time()
    res[key] = N_ACTIVE_VALIDATORS
    print(time.time()-t, "s for thread 8")

# 14, 15, 16 - min proposer bonus, max proposer bonus, community tax
def MyThread9(res):
    t = time.time()
    for key in CHAIN_DISTRIBUTION_PARAMS.keys():
        res[key] = CHAIN_DISTRIBUTION_PARAMS[key]
    print(time.time()-t, "s for thread 9")

# 18 - Rewards
def MyThread10(res, validator_addr, validator_index):
    t = time.time()
    res[f'val_{validator_index}_com_amt'] = get_rewards_current(validator_addr)
    print(time.time()-t, "s for thread 10")

def get_all_block_data(LATEST_BLOCK, _block_signatures, _timestamp, _proposer_addr):
    t = time.time()
    print(bcolors.OKCYAN, "BLOCK ", LATEST_BLOCK, bcolors.ENDC)
    result = {}
    all_threads = [
        threading.Thread(target=MyThread0, args=[result, LATEST_BLOCK]),
        threading.Thread(target=MyThread1, args=[result, "inflation_rate"]),
        threading.Thread(target=MyThread2, args=[result, "percent_staked"]),
        threading.Thread(target=MyThread3, args=[result, "total_block_fees", LATEST_BLOCK]),
        threading.Thread(target=MyThread4, args=[result, "proposer", _proposer_addr]),
        threading.Thread(target=MyThread4, args=[result, "timestamp", _timestamp]),
        threading.Thread(target=MyThread5, args=[result, "sign_ratio", _block_signatures]),
        threading.Thread(target=MyThread6, args=[result, "atom_staked_v"]),
        threading.Thread(target=MyThread7, args=[result, "total_supply"]),
        threading.Thread(target=MyThread9, args=[result])
    ]

    for val_ind, validator in enumerate(VALIDATOR_ADDRESS):
        all_threads.append(threading.Thread(target=MyThread10, args=[result, validator, val_ind]))

    for thread in all_threads:
        thread.start()
    for thread in all_threads:
        thread.join()

    dir_path = dir_path = os.path.dirname(os.path.realpath(__file__))+ f'/single_validators/{datafile_name}.csv'
    print(bcolors.OKGREEN, "result for block ", LATEST_BLOCK," : ", bcolors.ENDC, result)
    try:
        df = pd.read_csv(dir_path)
    except:
        df = pd.DataFrame()
    df_ls = df.to_dict('records')
    df_ls.append(result)
    pd.DataFrame(df_ls).to_csv(dir_path, index=False)

    print(bcolors.OKCYAN, "Time taken for block : ", LATEST_BLOCK, ": ", time.time() - t, bcolors.ENDC)
    print()


past_block_num = 0
new_block = 0
num_signatures = 0
time_stamp = 0
got_blocks=0
threads_to_stop = []
while(got_blocks < N_BLOCKS_TO_GET):
    print("beginning thread ", got_blocks)
    while past_block_num == new_block:
        resp = requests.get(RPC_URL+'/cosmos/base/tendermint/v1beta1/blocks/latest', headers=headers).json() # gets latest block number
        new_block = int(resp['block']['header']['height'])
        print(new_block)
        block_signatures=resp['block']['last_commit']['signatures']
        time_stamp = resp['block']['header']['time']
        proposer_addr = resp['block']['header']['proposer_address']
        time.sleep(0.5)

    new_block_thread = threading.Thread(target=get_all_block_data, args = [new_block, block_signatures, time_stamp, proposer_addr])
    print("started thread ", got_blocks)
    new_block_thread.start()
    print("ended thread", got_blocks)
    threads_to_stop.append(new_block_thread)

    past_block_num = new_block
    got_blocks+=1

print("End of Data Collection")


for i in threads_to_stop:
    i.join()

# 
# Getting block fees for extracted blocks 
#

print("Getting block fees for previous blocks")
dir_path = os.path.dirname(os.path.realpath(__file__))+f'/single_validators/{datafile_name}.csv'
df= pd.read_csv(dir_path)

for i in tqdm(range(len(df))):
    block_num = df.iloc[i]['block_num']
    row = df.iloc[i] 
    row['total_block_fees'] = get_total_fees(block_num)
    df.iloc[i] = row
    df.to_csv(dir_path, index=False)
    time.sleep(3)

# 
# Post processing
#

dir_path = os.path.dirname(os.path.realpath(__file__))+f'/single_validators/{datafile_name}-processed.csv'
processed_df = post_process_data(df, len(VALIDATOR_ADDRESS))
processed_df.to_csv(dir_path, index=False)