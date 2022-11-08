# The main file that is supposed to parse through all the blocks information and will output a CSV file
# containing information about signatures for each block in the `./block_signatures/` folder
import json
import os
import pandas as pd

START_BLOCK = 12763286
END_BLOCK = 12763590

class bcolors:
    OKCYAN = '\033[96m'
    WARNING = '\033[93m'
    ENDC = '\033[0m'

dir_path = os.path.dirname(os.path.realpath(__file__))+'/bech32_to_hex.json'
bech32_to_hex = json.load(fp=open(dir_path))
hex_to_bech32 = {v:k for k,v in bech32_to_hex.items()}

dir_path = os.path.dirname(os.path.realpath(__file__))+'/active_vals.json'
all_stakes = json.load(fp=open(dir_path))
operator_to_stake = {}
for i in all_stakes:
    operator_to_stake[i['operator_address']] = i['tokens']

columns = ['block_number']
df_ls = []
dir_path = os.path.dirname(os.path.realpath(__file__))+'/active_vals.json'
all_addresses = [val['operator_address'] for val in json.load(open(dir_path))]

for block in range(START_BLOCK, END_BLOCK+1):
    all_validator_keys = {}
    row = {}
    row['block_num'] = block

    # get participations for this block in all_validator_keys
    dir_path = os.path.dirname(os.path.realpath(__file__))+'/block_signatures/'+str(block)+'.json'
    
    with open(dir_path) as f:
        data = json.load(f)
        for signature in data:
            try:
                if signature['block_id_flag'] == 2:
                    op_addr = hex_to_bech32[signature['validator_address']]
                    all_validator_keys[op_addr] = 1
                elif signature['validator_address'] == '':
                    pass
                else:
                    op_addr = hex_to_bech32[signature['validator_address']]
                    all_validator_keys[op_addr] = 0
            except:
                print("No corresponding bech32 for ", signature)

        json.dump(all_validator_keys, open("all_validator_keys.json", "w+"))
    # iterate over validators and fill two columns for stake and vote

    errors = 0
    for ind, operator_address in enumerate(all_addresses):
        try:
            row['stake_'+str(ind)] = operator_to_stake[operator_address]
            row['vote_'+str(ind)] = all_validator_keys[operator_address]
        except:
            errors+=1
            row['stake_'+str(ind)] = operator_to_stake[operator_address]
            row['vote_'+str(ind)] = 0
            print(operator_address)
    print(bcolors.WARNING, 'Total errors in block: ', block, " : ", errors, bcolors.ENDC)
    df_ls.append(row)

dir_path = os.path.dirname(os.path.realpath(__file__))+'/participation.csv'
pd.DataFrame(df_ls).to_csv(dir_path, index=False)