# Cosmos staking data extraction pipeline

This is a repository intended for extractign basic data about Solana validators. 


Curl request to get inflation: curl -X GET "https://api.cosmos.network/cosmos/mint/v1beta1/inflation" -H  "accept: application/json"

For running the data extractor, follow the steps:
1. Clone this repo `git clone https://github.com/MakC-Ukr/cosmos-staking-data-extraction`
2. Install Python requirements `pip3 install -r requirements.txt`
5. Run extractor: `python3 main.py`



TOP20_VALIDATORS = [
    'cosmosvaloper1c4k24jzduc365kywrsvf5ujz4ya6mwympnc4en', # Coinbase Custody
    'cosmosvaloper156gqf9837u7d4c4678yt3rl4ls9c5vuursrrzf', # Binance Staking
    'cosmosvaloper1sjllsnramtg3ewxqwwrwjxfgc4n4ef9u2lcnj0', # stake.fish
    'cosmosvaloper14lultfckehtszvzw4ehu0apvsr77afvyju5zzy', # Dokia Fish
    'cosmosvaloper196ax4vc0lwpxndu9dyhvca7jhxp70rmcvrj90c', # SG-1
    'cosmosvaloper1z8zjv3lntpwxua0rtpvgrcwl0nm0tltgpgs6l7', # Kraken
    'cosmosvaloper1v5y0tg0jllvxf5c3afml8s3awue0ymju89frut', # Zero Knowledge Validator
    'cosmosvaloper1qaa9zej9a0ge3ugpx3pxyx602lxh3ztqgfnp42', # Game
    'cosmosvaloper1tflk30mq5vgqjdly92kkhhq3raev2hnz6eete3', # Everstake
    'cosmosvaloper19lss6zgdh5vvcpjhfftdghrpsw7a4434elpwpu', # Paradigm
    'cosmosvaloper1ey69r37gfxvxg62sh4r0ktpuc46pzjrm873ae8', # Sikka
    'cosmosvaloper14k4pzckkre6uxxyd2lnhnpp8sngys9m6hl6ml7', # Polychain
    'cosmosvaloper1hjct6q7npsspsg3dgvzk3sdf89spmlpfdn6m9d', # Figment
    'cosmosvaloper1clpqr4nrk4khgkxj78fcwwh6dl3uw4epsluffn', # Cosmostation
    'cosmosvaloper132juzk0gdmwuxvx4phug7m3ymyatxlh9734g4w', # P2P.ORG - P2P Validator
    'cosmosvaloper15urq2dtp9qce4fyc85m6upwm9xul3049e02707', # Chorus One
    'cosmosvaloper1vf44d85es37hwl9f4h9gv0e064m0lla60j9luj', # MultiChain ventures
    'cosmosvaloper1lzhlnpahvznwfv4jmay2tgaha5kmz5qxerarrl', # Citadel.one
    'cosmosvaloper1zqgheeawp7cmqk27dgyctd80rd8ryhqs6la9wc', # NO! Fee to 2025 💸 | melea.xyz
    'cosmosvaloper1g48268mu5vfp4wk7dk89r0wdrakm9p5xk0q50k', # Provalidator
    'cosmosvaloper1svwt2mr4x2mx0hcmty0mxsa4rmlfau4lwx2l69', # Twinstake Validator
    'cosmosvaloper1uxlf7mvr8nep3gm7udf2u9remms2jyjqvwdul2', # Kiln.fi
]