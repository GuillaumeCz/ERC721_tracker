import json
import asyncio
import time

from web3.auto import w3


def get_abi(_abi_uri):
    with open(_abi_uri, "r") as myFile:
        data = myFile.read()
    simple_token_json = json.loads(data)
    return simple_token_json['abi']


def is_address_null(_address):
    return int(_address, 16) == 0


class NameSystem:
    address_to_name = {}

    def get_user_by_address(self, _address):
        if is_address_null(_address):
            return '0x'
        return self.address_to_name[_address]

    def get_user_list_by_address_list(self, _addresses):
        names = []
        for address in _addresses:
            if not is_address_null(address):
                names.append(self.get_user_by_address(address))
        return names

    def __init__(self):
        self.address_to_name["0xFFcf8FDEE72ac11b5c542428B35EEF5769C409f0"] = "Joe"
        self.address_to_name["0x22d491Bde2303f2f43325b2108D26f1eAbA1e32b"] = "Bill"


class SimpleToken:
    # dict{ address: set(tokenId) }
    balances = {}

    def process_entries(self, _filter):
        for entry in _filter.get_all_entries():
            self.process_entry(entry)

    def process_entry(self, _entry):
        print('- processing...')
        token_id = _entry['args']['tokenId']
        user_from = _entry['args']['from']
        user_to = _entry['args']['to']

        if not is_address_null(user_from):
            self.balances[user_from].remove(token_id)

        if not is_address_null(user_to):
            if user_to not in self.balances:
                self.balances[user_to] = set([])
            self.balances[user_to].add(token_id)

        u_from = self.ns_instance.get_user_by_address(user_from)
        u_to = self.ns_instance.get_user_by_address(user_to)
        print('from', u_from, 'to', u_to, 'token', token_id)

    def get_token_list(self):
        tokens = set([])
        for user in self.balances:
            tokens.update(self.balances[user])
        return tokens

    def get_user_addresses(self):
        return self.balances.keys()

    async def async_listen(self, _event_filter, _poll_interval):
        print("Listening...")
        while True:
            for event in _event_filter.get_new_entries():
                self.process_entry(event)
            await asyncio.sleep(_poll_interval)

    def sync_listen(self, _event_filter, _poll_interval):
        print("Listening...")
        while True:
            for event in _event_filter.get_new_entries():
                self.process_entry(event)
            time.sleep(_poll_interval)

    def __init__(self, _address, _abi_location, _name_system_instance):
        self.ns_instance = _name_system_instance

        abi = get_abi(_abi_location)
        simple_token_contract = w3.eth.contract(abi=abi, address=_address)
        w3_filter = simple_token_contract.events.Transfer.createFilter(fromBlock=0)

        self.process_entries(w3_filter)
        self.users = self.get_user_addresses()
        self.tokens = self.get_token_list()

        # - sync -
        self.sync_listen(w3_filter, 1)

        # - async -
        # loop = asyncio.get_event_loop()
        # try:
        #     loop.run_until_complete(
        #         self.async_listen(self.filter, 1)
        #     )
        # finally:
        #     loop.close()


contract_address = "0xCfEB869F69431e42cdB54A4F4f105C19C080A601"
contract_abi_location = './SimpleToken.json'

ns = NameSystem()
simple_token = SimpleToken(contract_address, contract_abi_location, ns)

# print('# ', simple_token.balances)
# print('## ', simple_token.users)
# accounts = ns.get_user_list_by_address_list(simple_token.users)
# print('## - ', accounts)
# print('### ', simple_token.tokens)
