import time
t = time.time()
# import asyncio
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

async def bar(i):
    print("Starting i:", i)
    x = 0
    if(i == 0):
        x = get_supply_bonded_ratio()[0]
    elif(i == 1):
        x = get_inflation()
    elif(i == 2):
        x = get_fees_collected(LATEST_BLOCK)
    elif(i == 3):
        x = get_activeValidators_and_time(LATEST_BLOCK)[1]
    elif(i == 4):
        x = get_precommit_ratio(LATEST_BLOCK)
    elif(i == 5):
        x = get_validator_stake(VALIDATOR_ADDRESS)
    elif(i == 6):
        x = get_supply_bonded_ratio()[1]
    elif(i == 7):
        x = get_n_active_validators() # will mostly return 175
    print("Ending i:", i)
    return x

# async def main():
#     values = await asyncio.gather(*[bar(i) for i in range(TOTAL_ATTRIBUTES)])
#     values.insert(0, LATEST_BLOCK)
#     single_row = list_to_dict(values, COLUMN_NAMES)
#     df_ls.append(single_row)
#     pd.DataFrame(df_ls).to_csv('data.csv', index=False)
#     return True

# asyncio.run(main())
# print("Time taken: ", time.time() - t)

def threaded_function():
    for i in range(TOTAL_ATTRIBUTES):
        print("running")
        sleep(1)


if __name__ == "__main__":
    thread = Thread(target = threaded_function)
    thread.start()
    thread.join()
    print("thread finished...exiting")