# This file is supposed to get the list of all active validators and return their 
# respective rewards (commission/%commision) for the block number mentioned
import requests
from tqdm import tqdm
import json
import os
import base64
import pandas as pd
import time

START_BLOCK = 12763578
END_BLOCK = 12763590

headers = {'accept': 'application/json'}

class bcolors:
    OKCYAN = '\033[96m'
    WARNING = '\033[93m'
    ENDC = '\033[0m'

# get the list of operator addresses for 175 active validators
columns = ['block_number']
df_ls = []
dir_path = os.path.dirname(os.path.realpath(__file__))+'/active_vals.json'
all_addresses = [val['operator_address'] for val in json.load(open(dir_path))]
assert len(all_addresses) == 175

def get_rewards(BLOCK):
    val_rewards = {}
    url = f'https://rpc-cosmoshub.blockapsis.com/block_results?height={BLOCK}'
    response = requests.get(url=url, headers=headers)
    begin_block_events = response.json()['result']['begin_block_events']
    for event in begin_block_events:
        if event['type'] == "rewards"  or event['type'] == "commission":
            if len(event['attributes']) != 2:
                print(bcolors.WARNING, "skipping block with diff shape. Type: ", event['type'], bcolors.ENDC)
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
                    if key0 == "amount" and key1 == "validator":
                        val_rewards[value1] = value0
                except TypeError:
                    # print(bcolors.WARNING, "Error 1: check file code", bcolors.ENDC)
                    # Probably "argument should be a bytes-like object or ASCII string, not 'NoneType'"
                    # Probably missing key or value
                    pass
    return val_rewards


df_ls = []
dir_path = os.path.dirname(os.path.realpath(__file__))+'/active_val_rewards.csv'
df = pd.read_csv(dir_path)
df.sort_values(by=['block_number'], inplace=True)
if len(df) > 0:
    assert df.iloc[-1]['block_number'] == START_BLOCK-1 # if dataframe is not empty check if the last block number is the previous block and we continue from there
df_ls = df.to_dict('records')

for i in tqdm(range(START_BLOCK, END_BLOCK+1)):
    val_rewards = get_rewards(str(i+1)) # Note that we are passign the next block number because rewards for current block are acrued in the consecutively next block
    row = {}
    row['block_number'] = i
    for ind_addr, addr in enumerate(all_addresses):
        row['val_'+str(ind_addr)] = val_rewards[addr][:-4] # remove the last 4 characters which are the denom
    df_ls.append(row)
    pd.DataFrame(df_ls).to_csv(dir_path, index= False)
    time.sleep(3)