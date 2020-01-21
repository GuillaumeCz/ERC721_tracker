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


def timestamp_to_iso(_timestamp):
    return time.ctime(_timestamp)


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


class User:
    def __init__(self, _address, _name=None):
        if _name is not None:
            self.name = _name
        self.address = _address
        self.balance = set([])

    def __repr__(self):
        return str(self.__dict__)


class Transfer:
    @staticmethod
    def get_timestamp(_block_number):
        block = w3.eth.getBlock(_block_number)
        timestamp = block.timestamp
        return timestamp_to_iso(timestamp)

    def __init__(self, _entry):
        self.emitter = _entry['args']['from']
        self.receiver = _entry['args']['to']
        self.token_id = _entry['args']['tokenId']
        self.block_number = _entry['blockNumber']

    def __repr__(self):
        return str(self.__dict__)


class SimpleToken:
    transfers = []
    users = {}

    def process_entries(self, _filter):
        for entry in _filter.get_new_entries():
            self.process_entry(entry)

    def process_entry(self, _entry):
        token_id = _entry['args']['tokenId']
        user_from = _entry['args']['from']
        user_to = _entry['args']['to']

        if not is_address_null(user_from):
            self.users[user_from].balance.remove(token_id)

        if not is_address_null(user_to):
            if user_to not in self.users:
                self.users[user_to] = User(user_to)
            self.users[user_to].balance.add(token_id)

        self.transfers.append(Transfer(_entry))

    def get_token_list(self):
        tokens = set([])
        for user in self.users:
            tokens.update(self.users[user].balance)
        return tokens

    def get_user_addresses(self):
        return self.users.keys()

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

    def get_past_transactions(self, _filter):
        for entry in _filter.get_all_entries():
            self.process_entry(entry)

    def __init__(self, _address, _abi_location, _name_system_instance, _w3):
        self.ns_instance = _name_system_instance
        self.w3 = _w3

        abi = get_abi(_abi_location)
        simple_token_contract = self.w3.eth.contract(abi=abi, address=_address)
        w3_filter = simple_token_contract.events.Transfer.createFilter(fromBlock=0)

        self.process_entries(w3_filter)
        self._users = self.get_user_addresses()
        self.tokens = self.get_token_list()

        # - past -
        self.get_past_transactions(w3_filter)

        # - sync -
        # self.sync_listen(w3_filter, 1)

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
simple_token = SimpleToken(contract_address, contract_abi_location, ns, w3)

print('# ', simple_token.get_token_list())
print('## ', simple_token.get_user_addresses())

# print('# ', simple_token.users)
# print('## ', simple_token.transfers)

accounts = ns.get_user_list_by_address_list(simple_token.get_user_addresses())
print('## - ', accounts)
# print('### ', simple_token.tokens)
