from helpers import get_validator_stake
import requests
RPC_URL = 'https://cosmos-mainnet-rpc.allthatnode.com:1317'
headers={'content-Type': 'application/json'}

print(get_validator_stake('cosmosvaloper1svwt2mr4x2mx0hcmty0mxsa4rmlfau4lwx2l69'))