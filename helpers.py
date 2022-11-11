import pandas as pd
import time
import requests
import numpy as np
import time
import json
import os
from collections import defaultdict
from dotenv import load_dotenv
# from threading import Thread 
from random import sample

# Load env variables
load_dotenv()
MAX_TXNS_PER_BLOCK = 50
RPC_URL = os.getenv('RPC_URL')
RPC_URL_3 = os.getenv('RPC_URL_3')
COSMOSCAN_API = os.getenv('COSMOSCAN_API')
headers = {'accept': 'application/json',}
CMC_headers = {
    'X-CMC_PRO_API_KEY': '98c35ce7-275c-46d3-9221-1c08ae3caf3f',
    'Accept': 'application/json',
}
# N_ACTIVE_VALIDATORS = int(requests.get(RPC_URL+'/validatorsets/latest', headers=headers).json()['result']['total'])
# print("n_active_validators: ", N_ACTIVE_VALIDATORS)
##
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def get_inflation():    
    response = requests.get(RPC_URL+'/cosmos/mint/v1beta1/inflation', headers=headers).json()
    return response['inflation']

# @param - block_num can be supplied to get the data for a specific block. if the paramter is not specified the function returns the data fro the latest block.
def get_timestamp(block_number = -1):    
    if block_number == -1:
        response = requests.get(RPC_URL+'/cosmos/base/tendermint/v1beta1/blocks/latest', headers=headers).json()
    else:
        response = requests.get(RPC_URL+'/cosmos/base/tendermint/v1beta1/blocks/'+str(block_number), headers=headers).json()
    block_timestamp = response['block']['header']['time']
    return block_timestamp


def get_supply_bonded_ratio():
    params = {
        'by': 'hour',
    }
    bond_ratio = requests.get('https://api.cosmoscan.net/bonded-ratio/agg', params=params, headers=headers).json()[-1]['value']
    return bond_ratio

# returns total validator set size (425)
def get_n_validators():
    response = requests.get(COSMOSCAN_API+'/validators', headers=headers).json()     
    return len(response)
    
def get_n_active_validators():
    validator_set = requests.get(RPC_URL_3+'/validatorsets/latest', headers=headers).json()['result']['total']
    return int(validator_set)

def get_validator_stake(validator_addr):    
    stake_val = requests.get(COSMOSCAN_API+'/validator/'+validator_addr, headers=headers).json()['power']
    return stake_val

# 2 API requests are made inside this function
def get_precommit_ratio(num_signatures):
    response = len(requests.get(RPC_URL+'/blocks/'+str(num_signatures), headers=headers).json()['block']['last_commit']['signatures'])
    return ratio

# returns a dictionary containing: community tax to be paid, miniumum proposer bonus, and maximum proposer bonus
def get_chain_distribution_parameters():
    response = requests.get(RPC_URL+'/distribution/parameters', headers=headers).json()['result']
    result_dict = {}
    result_dict['community_tax'] = response['community_tax']
    result_dict['min_proposer_bonus'] = response['base_proposer_reward']
    result_dict['max_proposer_bonus'] = response['bonus_proposer_reward']
    return result_dict

# returns a dictionary of information: block number, denomination fo rewards, rewards accrued based on self-stake and based on delegation stakes
def get_rewards(validator_addr):
    # response = requests.get(RPC_URL+'/distribution/validators/'+validator_addr, headers=headers).json()
    # result_dict = {}
    # response = response['result']
    # result_dict['self_bonded_rew_amt'] = response['self_bond_rewards'][0]['amount']
    # result_dict['commission_amt'] = response['val_commission']['commission'][0]['amount']
    # return result_dict
    response = requests.get(RPC_URL+f'/cosmos/distribution/v1beta1/validators/{validator_addr}/commission', headers=headers).json()
    result_dict = {}
    response = response['commission']['commission'][0]['amount']
    # result_dict['self_bonded_rew_amt'] = response['self_bond_rewards'][0]['amount']
    result_dict['commission_amt'] = response
    print(result_dict)
    return result_dict

def list_to_dict(ls, keys):
    d = {}
    for i in range(len(ls)):
        d[keys[i]] = ls[i]
    return d

def get_total_supply():
    response = requests.get(RPC_URL+'/cosmos/bank/v1beta1/supply/uatom', headers=headers).json()['amount']['amount']
    return response

def get_block_time(bl_num):
    response = requests.get(RPC_URL+'/blocks/'+str(bl_num), headers=headers).json()['block']['header']['time']
    return response

# def get_fees_collected(block_number):    
#     params = {
#         'limit': '30',
#     }
#     response = requests.get('https://api.cosmostation.io/v1/txs', params=params, headers=headers).json()
#     total_fees = 0

#     for tx in response:
#         act_block_height = tx['data']['height']
#         act_fee = float(tx['data']['tx']['auth_info']['fee']['amount'][0]['amount'])
#         if act_block_height == str(block_number):
#             total_fees+=act_fee
#     return total_fees

def get_total_fees(_block_num):
    params = {
        'events': 'tx.height='+str(_block_num),
        'pagination.limit': '20',
    }
    response = requests.get('https://api.cosmos.network/cosmos/tx/v1beta1/txs', params=params, headers=headers).json()['tx_responses']
    total_fees = 0
    for i in response:
        total_fees += int(i['tx']['auth_info']['fee']['amount'][0]['amount'])
    return total_fees

def get_validator_commission(validator_addr):
    response = requests.get(RPC_URL+f'/cosmos/staking/v1beta1/validators/{validator_addr}', headers=headers).json()['validator']['commission']['commission_rates']['rate']
    response = float(response)*100
    return response

# @param ls_valid requires the list of validators for which the commission and stake is to be returned
def get_ALL_validators_info(ls_valid):
    res_dict = {}
    all_info = requests.get(COSMOSCAN_API+'/validators', headers=headers).json()

    index = 1
    for val_addr in ls_valid:
        for info in all_info:
            if val_addr == info['operator_address']:
                res_dict["v"+str(index)+"_title"] = info['title']
                res_dict["v"+str(index)+"_id"] = val_addr
                res_dict["v"+str(index)+"_comsn"] = info['fee']
                res_dict["v"+str(index)+"_stake"] = info['power']
                index+=1
                break
    return res_dict

# returns the sum of active validators' stake and inactive validators' stake (in ATOM)
def get_active_stake_vs_inactive():
    all_info = requests.get(COSMOSCAN_API+'/validators', headers=headers).json()
    stakes = []
    for i in range(len(all_info)):
        stakes.append(float(all_info[i]['power']))
    stakes = np.array(stakes)
    stakes.sort()
    active_sum = stakes[-175:].sum()
    inactive_sum = stakes[:-175].sum()
    return active_sum, inactive_sum

# @desc returns the signing ratio for a block
# @param block_signatures - an array of signatures for a block
# @param n_act_validators - number of active validators on the network
def get_sign_ratio_from_signatures_array(block_signatures, n_act_validators):
    count=0
    for i in block_signatures:
        if i['block_id_flag'] == 'BLOCK_ID_FLAG_COMMIT':
            count+=1
    return count/n_act_validators

# @desc returns the array of signatures from each active validator for a specific block number
# @param _block_num - the height of the block for which the signatures are to be returned
def get_signatures(_block_num):
    url = RPC_URL+f'/blocks/{_block_num}'
    block_info = requests.get(url, headers=headers).json()['block']['last_commit']['signatures']
    return block_info

print(get_block_time(12763524))