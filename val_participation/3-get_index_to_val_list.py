# Used to get the mapping from validator address to index in the dataframe
import pandas as pd
import requests
import json
import os
import base64
from dotenv import load_dotenv
import time

dir_path = os.path.dirname(os.path.realpath(__file__))+'/active_vals.json'
all_addresses = [val['operator_address'] for val in json.load(open(dir_path))]
dir_path = os.path.dirname(os.path.realpath(__file__))+'/val_index.csv'
pd.DataFrame(all_addresses).to_csv(dir_path, index=False)