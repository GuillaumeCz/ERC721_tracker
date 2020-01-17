import json
import asyncio

from web3.auto import w3


def get_abi(abi_uri):
    with open(abi_uri, "r") as myFile:
        data = myFile.read()
    simple_token_json = json.loads(data)
    return simple_token_json['abi']


def is_address_null(address):
    return int(address, 16) == 0


class SimpleToken:
    # dict{ address: set(tokenId) }
    balances = {}

    def process_entries(self, _filter):
        for entry in _filter.get_all_entries():
            self.process_entry(entry)

    def process_entry(self, entry):
        token_id = entry['args']['tokenId']
        user_from = entry['args']['from']
        user_to = entry['args']['to']

        if not is_address_null(user_from):
            self.balances[user_from].remove(token_id)

        if not is_address_null(user_to):
            if user_to not in self.balances:
                self.balances[user_to] = set([])
            self.balances[user_to].add(token_id)

    def get_token_list(self):
        tokens = set([])
        for user in self.balances:
            tokens.update(self.balances[user])
        return tokens

    def get_users(self):
        return self.balances.keys()

    async def listen(self, event_filter, poll_interval):
        print("Listening...")
        while True:
            for event in event_filter.get_new_entries():
                self.process_entry(event)
            await asyncio.sleep(poll_interval)

    def __init__(self, address, abi_location):
        self.abi = get_abi(abi_location)
        self.simple_token_contract = w3.eth.contract(abi=self.abi, address=address)
        self.filter = self.simple_token_contract.events.Transfer.createFilter(fromBlock=0)

        # self.process_entries(self.filter)
        # self.users = self.get_users()
        # self.tokens = self.get_token_list()

        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(
                self.listen(self.transfer_events, 1)
            )
        finally:
            loop.close()


contract_address = "0xCfEB869F69431e42cdB54A4F4f105C19C080A601"
contract_abi_location = './SimpleToken.json'

simple_token = SimpleToken(contract_address, contract_abi_location)

# print('# ', simple_token.balances)
# print('## ', simple_token.users)
# print('### ', simple_token.tokens)
