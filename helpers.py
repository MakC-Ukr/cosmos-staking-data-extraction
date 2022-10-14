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
def get_activeValidators_and_time(block_number = -1):    
    if block_number == -1:
        response = requests.get(RPC_URL+'/cosmos/base/tendermint/v1beta1/blocks/latest', headers=headers).json()
    else:
        response = requests.get(RPC_URL+'/cosmos/base/tendermint/v1beta1/blocks/'+str(block_number), headers=headers).json()
    n_act_v = len(response['block']['last_commit']['signatures'])
    block_timestamp = response['block']['header']['time']
    return (n_act_v, block_timestamp)


def get_supply_bonded_ratio():
    response = requests.get(RPC_URL+ '/cosmos/staking/v1beta1/pool', headers=headers).json()['pool']
    print(response)
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


def get_fees_collected(block_number = -1):    
    if block_number == -1:
        block_number = requests.get(RPC_URL+'/cosmos/base/tendermint/v1beta1/blocks/latest', headers=headers).json()['block']['header']['height'] # gets latest block number
        block_number = int(block_number)-2 # This is done since we need to allow Cosmoscan to update latest block as well
        response = requests.get(COSMOSCAN_API+'/block/'+str(block_number), headers=headers).json()['txs']
    else:
        response = requests.get(COSMOSCAN_API+'/block/'+str(block_number), headers=headers).json()['txs']
    
    fees_collected = 0
    for tx in response:
        fees_collected += float(tx['fee'])
    return fees_collected


def get_validator_stake(validator_addr):    
    validator_set = requests.get(COSMOSCAN_API+'/validators', headers=headers).json() 
    for val in validator_set:
        if val['acc_address'] == validator_addr:
            return int(float(val['power']))
    raise Exception('My_Exception: Validator not found')


def get_precommit_ratio(block_num):
    active_validators = get_n_active_validators()
    response = requests.get(RPC_URL+'/blocks/'+str(block_num), headers=headers).json()['block']['last_commit']['signatures']
    ratio = len(response)/active_validators
    return ratio

print(get_precommit_ratio(12444791))