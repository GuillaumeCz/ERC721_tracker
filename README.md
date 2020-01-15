# ERC721_tracker

Erc721 token tracker using web3 filters

Prerequisite
````bash
# launch a venv
. venv/bin/activate
# install requirements
pip install -r requirements.txt
````

1. Migrate & deploy the targeted contract to a test-rpc (ganache-like) 
2. Get the contract's ABI (`{contract}.json`) into the project (such as `SimpleToken.json`) 
3. Get the contract's address once deployed
4. Update both variables `contract_address` and `contract_abi_location` with what you get with steps 2 & 3

Run
````bash
python index.py
````
