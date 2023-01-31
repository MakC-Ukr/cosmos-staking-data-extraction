import threading
import time
import requests

headers = {"accept": "application/json"}
RPC_URL = "https://cosmos-mainnet-rpc.allthatnode.com:1317"
# def run():
#     while True:
#         print('thread running')
#         global stop_threads
#         if stop_threads:
#             break

# stop_threads = False
# t1 = threading.Thread(target = run)
# t1.start()
# time.sleep(1)
# stop_threads = True
# t1.join()
# print('thread killed')


def get_total_fees(_block_num):
    params = {
        "events": "tx.height=" + str(_block_num),
        "pagination.limit": "20",
    }
    response = requests.get(
        "https://api.cosmos.network/cosmos/tx/v1beta1/txs",
        params=params,
        headers=headers,
    ).json()["tx_responses"]
    total_fees = 0
    for i in response:
        total_fees += int(i["tx"]["auth_info"]["fee"]["amount"][0]["amount"])
    return total_fees


print(get_total_fees(12716914))
