import requests
import os
import base64
from dotenv import load_dotenv

headers = {'accept': 'application/json'}
load_dotenv()
VALIDATOR = 'cosmosvaloper1svwt2mr4x2mx0hcmty0mxsa4rmlfau4lwx2l69'
BLOCK = 12_689_264
ALLTHATNODE_API_KEY = os.getenv('ALLTHATNODE_API_KEY')

def get_rewards(val_address):
    url = f'https://cosmos-mainnet-rpc.allthatnode.com:26657/{ALLTHATNODE_API_KEY}/block_results?height={BLOCK}'
    print(f'Block result url: {url}')
    response = requests.get(url=url, headers=headers)
    begin_block_events = response.json()['result']['begin_block_events']
    for event in begin_block_events:
        if event['type'] == "rewards": # or event['type'] == "commission"
            if len(event['attributes']) != 2:
                print(f"Skipping event with wrong shape")
            else:
                a0 = event['attributes'][0]
                a1 = event['attributes'][1]
                try:
                    key0 = base64.b64decode(a0['key']).decode("utf-8")
                    value0 = base64.b64decode(a0['value']).decode("utf-8")
                    key1 = base64.b64decode(a1['key']).decode("utf-8")
                    value1 = base64.b64decode(a1['value']).decode("utf-8")
                    if key0 == "amount" and key1 == "validator" and value1 == val_address:
                        print(f"{value0} paid to our validator")
                except TypeError:
                    # Probably "argument should be a bytes-like object or ASCII string, not 'NoneType'"
                    # print("  Missing key or value")
                    pass

def main():
    get_rewards(VALIDATOR)

if __name__ == "__main__":
    main()