import os
import pandas as pd
from tqdm import tqdm
import json
import requests
import time
from helpers import get_total_fees, headers, post_process_data

dir_path = os.path.dirname(os.path.realpath(__file__))+'/single_validators/multiple.csv'
df= pd.read_csv(dir_path)

for i in tqdm(range(len(df))):
    block_num = df.iloc[i]['block_num']
    row = df.iloc[i] 
    row['total_block_fees'] = get_total_fees(block_num)
    df.iloc[i] = row
    df.to_csv(dir_path, index=False)
    time.sleep(3)

processed_df = post_process_data(df)
processed_df.to_csv(dir_path, index=False)