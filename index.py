import json
import time

from web3.auto import w3


def get_abi(abi_uri):
    with open(abi_uri, "r") as myFile:
        data = myFile.read()
    simple_token_json = json.loads(data)
    return simple_token_json['abi']


def is_address_null(address):
    return int(address, 16) == 0


class SimpleToken:
    def update_balances(self):
        # dict{ address: set(tokenId) }
        user_balances = {}

        for entry in self.transfers:
            token_id = entry['args']['tokenId']
            user_from = entry['args']['from']
            user_to = entry['args']['to']

            if user_from not in user_balances and not is_address_null(user_from):
                user_balances[user_from] = {token_id}

            if not is_address_null(user_from) and token_id in user_balances[user_from]:
                user_balances[user_from].remove(token_id)

            if user_to not in user_balances and not is_address_null(user_to):
                user_balances[user_to] = set([])

            if not is_address_null(user_to):
                user_balances[user_to].add(token_id)

        return user_balances

    def get_token_list(self):
        tokens = set([])
        for user in self.balances:
            tokens.update(self.balances[user])
        return tokens

    def listen(self, event_filter, poll_interval):
        while True:
            for event in event_filter.get_new_entries():
                print("New event", event)
                print("#######")
            time.sleep(poll_interval)

    def __init__(self, address, abi_location):
        self.abi = get_abi(abi_location)
        self.simple_token_contract = w3.eth.contract(abi=self.abi, address=address)
        self.transfer_events = self.simple_token_contract.events.Transfer.createFilter(fromBlock=0)
        self.transfers = self.transfer_events.get_all_entries()

        self.balances = self.update_balances()
        self.users = self.balances.keys()
        self.tokens = self.get_token_list()

        self.listen(self.transfer_events, 1)


contract_address = "0xCfEB869F69431e42cdB54A4F4f105C19C080A601"
contract_abi_location = './SimpleToken.json'

simple_token = SimpleToken(contract_address, contract_abi_location)

# print('# ', simple_token.balances)
# print('## ', simple_token.users)
# print('### ', simple_token.tokens)
