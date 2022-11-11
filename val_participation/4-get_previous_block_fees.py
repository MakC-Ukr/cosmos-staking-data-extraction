import os
import pandas as pd
from tqdm import tqdm
import json
import requests
import time

START_BLOCK = 12788591
END_BLOCK = 12788614

headers = {'accept': 'application/json'}
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

dir_path = os.path.dirname(os.path.realpath(__file__))+'/prev_block_fees.csv'
df_ls = []
df = pd.read_csv(dir_path)
df.sort_values(by=['block_num'], inplace=True)
if len(df) > 0:
    assert df.iloc[-1]['block_num'] == START_BLOCK-1 # if dataframe is not empty check if the last block number is the previous block and we continue from there
df_ls = df.to_dict('records')


for i in tqdm(range(START_BLOCK, END_BLOCK+1)):
    row = {}
    row['block_num'] = i
    row["block_fees"] = get_total_fees(i)
    df_ls.append(row)
    pd.DataFrame(df_ls).to_csv(dir_path, index=False)
    time.sleep(5)