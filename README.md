# Cosmos staking data extraction pipeline

This is a repository intended for extractign basic data about Solana validators. 


Curl request to get inflation: curl -X GET "https://api.cosmos.network/cosmos/mint/v1beta1/inflation" -H  "accept: application/json"

For running the data extractor, follow the steps:
1. Clone this repo `git clone https://github.com/MakC-Ukr/cosmos-staking-data-extraction`
2. Install Python requirements `pip3 install -r requirements.txt`
5. Run extractor: `python3 main.py`