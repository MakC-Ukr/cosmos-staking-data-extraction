import time
import threading
import pandas as pd
import os
from threading import Thread
from time import sleep
from dotenv import load_dotenv
import requests
from helpers import (
    bcolors,
    get_rewards,
    get_block_time,
    get_total_supply,
    get_ALL_validators_info,
    get_chain_distribution_parameters,
    get_supply_bonded_ratio,
    get_n_validators,
    get_n_active_validators,
    get_total_fees,
    get_timestamp,
    get_validator_stake,
    get_precommit_ratio,
    headers,
    get_inflation,
    list_to_dict,
    get_validator_commission,
)
from postprocess_data import post_process_data

# Loading prerequisites
load_dotenv()
df = pd.read_csv("data.csv")
df_ls = df.to_dict("records")
COLUMN_NAMES = list(df.columns)
RPC_URL = os.getenv("RPC_URL")
BLOCKS_TO_RUN_FOR = 300  # 10 mins = ~100 blocks


TOP20_VALIDATORS = [
    # 'cosmosvaloper1c4k24jzduc365kywrsvf5ujz4ya6mwympnc4en', # Coinbase Custody
    # 'cosmosvaloper156gqf9837u7d4c4678yt3rl4ls9c5vuursrrzf', # Binance Staking
    # 'cosmosvaloper1sjllsnramtg3ewxqwwrwjxfgc4n4ef9u2lcnj0', # stake.fish
    # 'cosmosvaloper14lultfckehtszvzw4ehu0apvsr77afvyju5zzy', # Dokia Fish
    # 'cosmosvaloper196ax4vc0lwpxndu9dyhvca7jhxp70rmcvrj90c', # SG-1
    # 'cosmosvaloper1z8zjv3lntpwxua0rtpvgrcwl0nm0tltgpgs6l7', # Kraken
    # 'cosmosvaloper1v5y0tg0jllvxf5c3afml8s3awue0ymju89frut', # Zero Knowledge Validator
    # 'cosmosvaloper1qaa9zej9a0ge3ugpx3pxyx602lxh3ztqgfnp42', # Game
    # 'cosmosvaloper1tflk30mq5vgqjdly92kkhhq3raev2hnz6eete3', # Everstake
    # 'cosmosvaloper19lss6zgdh5vvcpjhfftdghrpsw7a4434elpwpu', # Paradigm
    # 'cosmosvaloper1ey69r37gfxvxg62sh4r0ktpuc46pzjrm873ae8', # Sikka
    # 'cosmosvaloper14k4pzckkre6uxxyd2lnhnpp8sngys9m6hl6ml7', # Polychain
    # 'cosmosvaloper1hjct6q7npsspsg3dgvzk3sdf89spmlpfdn6m9d', # Figment
    # 'cosmosvaloper1clpqr4nrk4khgkxj78fcwwh6dl3uw4epsluffn', # Cosmostation
    # 'cosmosvaloper132juzk0gdmwuxvx4phug7m3ymyatxlh9734g4w', # P2P.ORG - P2P Validator
    # 'cosmosvaloper15urq2dtp9qce4fyc85m6upwm9xul3049e02707', # Chorus One
    # 'cosmosvaloper1vf44d85es37hwl9f4h9gv0e064m0lla60j9luj', # MultiChain ventures
    # 'cosmosvaloper1lzhlnpahvznwfv4jmay2tgaha5kmz5qxerarrl', # Citadel.one
    # 'cosmosvaloper1zqgheeawp7cmqk27dgyctd80rd8ryhqs6la9wc', # NO! Fee to 2025 💸 | melea.xyz
    # 'cosmosvaloper1g48268mu5vfp4wk7dk89r0wdrakm9p5xk0q50k', # Provalidator
    "cosmosvaloper1svwt2mr4x2mx0hcmty0mxsa4rmlfau4lwx2l69",  # Twinstake Validator
    # 'cosmosvaloper1uxlf7mvr8nep3gm7udf2u9remms2jyjqvwdul2', # Kiln.fi
]

# CONST VALUES - 9,10,11,12,13,17,21
BLOCKS_PRE_YEAR = 4360000
CONST_ATTRIBUTES = {
    "Block_length_target": (365 * 24 * 60 * 60) / BLOCKS_PRE_YEAR,
    "Goal_Bonded": 0.6666,
    "Inflation_Rate_Change": 0.13,
    "Min_Inflation_Rate": 0.07,
    "Max_Inflation_Rate": 0.20,
    "Min_Signatures": 0.6666,
    "Blocks_per_year": BLOCKS_PRE_YEAR,
}


# No API calls to get data
def MyThread0(res, _latest_block):
    res["block_num"] = _latest_block
    for key in CONST_ATTRIBUTES.keys():
        res[key] = CONST_ATTRIBUTES[key]


# 1 - INFLATION RATE
def MyThread1(res, key):
    res[key] = get_inflation()


# 0 - PERCENTAGE ATOM STAKED
def MyThread2(res, key):
    res[key] = get_supply_bonded_ratio()


# 2, 20 - Total_Fees_Per_Block and txFees
def MyThread3(res, key, _latest_block):
    res[key] = get_total_fees(_latest_block)


# 4 - block timestamp
def MyThread4(res, key, _latest_block):
    res[key] = get_timestamp(_latest_block)


# 5 - PRECOMMITS RATIO
def MyThread5(res, key, _latest_block):
    res[key] = get_precommit_ratio(_latest_block)


# 7 - TOTAL SUPPLY - THIS IS WRONG
def MyThread7(res, key):
    res[key] = get_total_supply()


# 8 - N ACTIVE VALIDATORS
def MyThread8(res, key):
    res[key] = get_n_active_validators()


# 14, 15, 16 - min proposer bonus, max proposer bonus, community tax
def MyThread9(res):
    result_dict = get_chain_distribution_parameters()
    for key in result_dict.keys():
        res[key] = result_dict[key]


# v1_stake - get info (stake+commission) for top20 validators
def MyThread6(res, validator_list):
    dict_res = get_ALL_validators_info(validator_list)
    for key in dict_res.keys():
        res[key] = dict_res[key]


#
# 20 threads for validator rewards
#

# Uncomment the following thread and run it if you have a validator set of about 3 validators running (will send API requests paralelly)
# also insert the code from below the thread into the get_all_block_data() function

# @param validator_addr - address of the validator for which we are fetching the rewards
# @param validator_index - index of the validator in TOP20_VALIDATORS for adding the prefix v1_, v2_ etc.
def MyThread_R1(res, validator_addr, validator_index):
    result_dict = get_rewards(validator_addr)
    for key in result_dict.keys():
        res["v" + str(validator_index) + key] = result_dict[key]


# Uncomment the following thread and run it if you have a small validator set (this will run the API calls sequentially)
# def MyThread_R1(res, val_ls):
#     validator_index = 1
#     for i in val_ls:
#         result_dict = get_rewards(i)
#         for key in result_dict.keys():
#             res["v"+ str(validator_index) + key] = result_dict[key]
#             validator_index+=1


def get_all_block_data(LATEST_BLOCK):
    result = {}

    all_threads = [
        threading.Thread(target=MyThread0, args=[result, LATEST_BLOCK]),
        threading.Thread(target=MyThread1, args=[result, "inflation_rate"]),
        threading.Thread(target=MyThread2, args=[result, "percent_staked"]),
        threading.Thread(
            target=MyThread3, args=[result, "total_block_fees", LATEST_BLOCK]
        ),
        threading.Thread(target=MyThread4, args=[result, "timestamp", LATEST_BLOCK]),
        threading.Thread(target=MyThread5, args=[result, "sign_ratio", LATEST_BLOCK]),
        threading.Thread(target=MyThread7, args=[result, "total_supply"]),
        threading.Thread(target=MyThread8, args=[result, "n_validators"]),
        threading.Thread(target=MyThread9, args=[result]),
        threading.Thread(target=MyThread6, args=[result, TOP20_VALIDATORS]),
        # threading.Thread(target=MyThread_R1, args=[result, TOP20_VALIDATORS])
    ]

    all_threads.extend(
        [
            threading.Thread(target=MyThread_R1, args=[result, validator_addr, i])
            for i, validator_addr in enumerate(TOP20_VALIDATORS)
        ]
    )

    t = time.time()
    for thread in all_threads:
        thread.start()

    for thread in all_threads:
        thread.join()

    df_ls.append(result)
    dir_path = os.path.abspath("") + "/data.csv"
    pd.DataFrame(df_ls).to_csv(dir_path, index=False)

    print(
        bcolors.OKCYAN,
        "Time taken for block : ",
        LATEST_BLOCK,
        ": ",
        time.time() - t,
        bcolors.ENDC,
    )
    print()


past_block_num = 0
new_block = 0

count_blocks = 0

# rewards_before_list = {}
# for ind, i in enumerate(TOP20_VALIDATORS):
#     done = False
#     while(not done):
#         try:
#             print(ind, ". ", i)
#             result_dict = get_rewards(i)
#             rewards_before_list[i] = result_dict
#             time.sleep(1)
#             done = True
#         except:
#             time.sleep(2)

while count_blocks < BLOCKS_TO_RUN_FOR:
    while past_block_num == new_block:
        new_block = int(
            requests.get(
                RPC_URL + "/cosmos/base/tendermint/v1beta1/blocks/latest",
                headers=headers,
            ).json()["block"]["header"]["height"]
        )  # gets latest block number
    print(bcolors.OKCYAN, "BLOCK ", new_block, bcolors.ENDC)
    get_all_block_data(new_block)
    past_block_num = new_block
    count_blocks += 1

# rewards_after_list = {}
# for ind, i in enumerate(TOP20_VALIDATORS):
#     done = False
#     while(not done):
#         try:
#             print(ind, ". ", i)
#             result_dict = get_rewards(i)
#             rewards_after_list[i] = result_dict
#             time.sleep(1)
#             done = True
#         except:
#             time.sleep((2))

# df_ls = []
# for i in TOP20_VALIDATORS:
#     df_ls.append({
#         "validator": i,
#         "self_bond": float(rewards_after_list[i]['self_bonded_rew_amt'])-float(rewards_before_list[i]['self_bonded_rew_amt']),
#         'commision': float(rewards_after_list[i]['commission_amt'])-float(rewards_before_list[i]['commission_amt']),
#     })

# dir_path = os.path.abspath('')+'/rewards20.csv'
# pd.DataFrame(df_ls).to_csv(dir_path, index=False)

# post_process_data()
