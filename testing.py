from helpers import get_rewards
import requests
RPC_URL = 'https://cosmos-mainnet-rpc.allthatnode.com:1317'
headers={'content-Type': 'application/json'}


def get_rewards(validator_addr):
    response = requests.get(RPC_URL+'/distribution/validators/'+validator_addr, headers=headers).json()
    result_dict = {}
    response = response['result']
    result_dict['self_bonded_rew_amt'] = response['self_bond_rewards'][0]['amount']
    result_dict['commission_amt'] = response['val_commission']['commission'][0]['amount']
    return result_dict

print(get_rewards('cosmosvaloper196ax4vc0lwpxndu9dyhvca7jhxp70rmcvrj90c'))