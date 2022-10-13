# Cosmos staking data extraction pipeline

This is a repository intended for extractign basic data about Solana validators. 


Curl request to get inflation: curl -X GET "https://api.cosmos.network/cosmos/mint/v1beta1/inflation" -H  "accept: application/json"

For running the data extractor, follow the steps:
1. Clone this repo `git clone https://github.com/MakC-Ukr/solana-data-extraction`
2. Install Python requirements `pip3 install -r requirements.txt`
3. Fill the `.env` file details as shown in `.env.example`
4. Rename `data-example.csv` to `data.csv`
5. Run extractor: `python3 main.py`