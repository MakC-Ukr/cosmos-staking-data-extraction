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

def get_inflation():    
    headers = {
        'accept': 'application/json',
    }
    response = requests.get(RPC_URL+'/cosmos/mint/v1beta1/inflation', headers=headers).json()
    return response['inflation']

# @param - block_num can be supplied to get the data for a specific block. if the paramter is not specified the function returns the data fro the latest block.
def get_activeValidators_and_time(block_number = -1):    
    headers = {
        'accept': 'application/json',
    }
    if block_number == -1:
        response = requests.get(RPC_URL+'/cosmos/base/tendermint/v1beta1/blocks/latest', headers=headers).json()
    else:
        response = requests.get(RPC_URL+'/cosmos/base/tendermint/v1beta1/blocks/'+str(block_number), headers=headers).json()
    n_act_v = len(response['block']['last_commit']['signatures'])
    block_timestamp = response['block']['header']['time']
    return (n_act_v, block_timestamp)



def get_supply_bonded_ratio():
    headers = {'accept': 'application/json'}
    response = requests.get(RPC_URL+ '/cosmos/staking/v1beta1/pool', headers=headers).json()['pool']
    print(response)
    total_sup = float(response['bonded_tokens']) +  float(response['not_bonded_tokens'])
    bond_ratio = float(response['bonded_tokens']) / total_sup
    return (total_sup, bond_ratio)

def get_n_validators():
    headers = {
    'accept': 'application/json',
    }
    response = requests.get(COSMOSCAN_API+'/validators', headers=headers).json()
    return len(response)
    

def get_fees_collected(block_number = -1):    
    headers = {
        'accept': 'application/json',
    }
    if block_number == -1:
        block_number = requests.get(RPC_URL+'/cosmos/base/tendermint/v1beta1/blocks/latest', headers=headers).json()['block']['header']['height']
        block_number = int(block_number)-2 # This is done since we need to allow Cosmoscan to update latest block as well
        response = requests.get('https://api.cosmoscan.net/block/'+str(block_number), headers=headers).json()['txs']
    else:
        response = requests.get('https://api.cosmoscan.net/block/'+str(block_number), headers=headers).json()['txs']
    
    fees_collected = 0
    for tx in response:
        fees_collected += float(tx['fee'])
    return fees_collected

print(get_fees_collected())

# with open("data.json", 'w+') as f:
#     json.dump(get_fees(N), f)

# print(get_total_supply())
# def get_total_supply():    
#     headers = {
#         'accept': 'application/json',
#     }
#     response = requests.get(RPC_URL+'/cosmos/bank/v1beta1/supply', headers=headers).json()
#     return response