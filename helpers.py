import pandas as pd
import time
import requests
import time
import json
import os
from collections import defaultdict
from dotenv import load_dotenv
# from threading import Thread 
from random import sample

# Load env variables
load_dotenv()
RPC_URL = os.getenv('RPC_URL')
COSMOSCAN_API = os.getenv('COSMOSCAN_API')
RANDOM_VALIDATOR_ADDRESS = 'cosmos1c4k24jzduc365kywrsvf5ujz4ya6mwymy8vq4q' # Coinbase custody validator
headers = {'accept': 'application/json',}

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
    response = requests.get(RPC_URL+ '/cosmos/staking/v1beta1/pool', headers=headers).json()['pool']
    total_sup = float(response['bonded_tokens']) +  float(response['not_bonded_tokens'])
    bond_ratio = float(response['bonded_tokens']) / total_sup
    return (total_sup, bond_ratio)

# returns total validator set size (425)
def get_n_validators():
    response = requests.get(COSMOSCAN_API+'/validators', headers=headers).json()     
    return len(response)
    
def get_n_active_validators():
    validator_set = requests.get(RPC_URL+'/validatorsets/latest', headers=headers).json()['result']['total']
    return int(validator_set)

def get_fees_collected(block_number=-1):    
    if block_number == -1:
        block_number = requests.get(RPC_URL+'/cosmos/base/tendermint/v1beta1/blocks/latest', headers=headers).json()['block']['header']['height'] # gets latest block number
        print("-1 passed")

    # following RPC API returns block info but does not include tx hashes or fees
    # response = requests.get('https://api.cosmos.network/blocks/'+str(block_number), headers=headers)
    # response = response.json()['block']['data']['txs']
    
    # Cosmoscan API returns number of txns but isn't currently returning txn data (probably server side error- because returns for very old blocks)
    response = requests.get(COSMOSCAN_API+'/block/'+str(block_number), headers=headers).json()['txs']
    fees_collected = 0
    if(response is None):
        print("No fees collected in block: ", block_number)
        return 0
    for tx in response:
        fees_collected += float(tx['fee'])
    return fees_collected

def get_validator_stake(validator_addr):    
    validator_set = requests.get(COSMOSCAN_API+'/validators', headers=headers).json() 
    for val in validator_set:
        if val['acc_address'] == validator_addr:
            return int(float(val['power']))
    raise Exception('My_Exception: Validator not found')

# 2 API requests are made inside this function
def get_precommit_ratio(block_num):
    active_validators = get_n_active_validators()
    response = requests.get(RPC_URL+'/blocks/'+str(block_num), headers=headers).json()['block']['last_commit']['signatures']
    ratio = len(response)/active_validators
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
    response = requests.get(RPC_URL+'/distribution/validators/'+validator_addr, headers=headers).json()
    result_dict = {}
    response = response['result']
    
    result_dict['self_bonded_denom'] = response['self_bond_rewards'][0]['denom']
    result_dict['self_bonded_amt'] = response['self_bond_rewards'][0]['amount']
    result_dict['commission_denom'] = response['val_commission']['commission'][0]['denom']
    result_dict['commission_amt'] = response['val_commission']['commission'][0]['amount']

    return result_dict

def list_to_dict(ls, keys):
    d = {}
    for i in range(len(ls)):
        d[keys[i]] = ls[i]
    return d

print(get_rewards('cosmos1c4k24jzduc365kywrsvf5ujz4ya6mwymy8vq4q'))