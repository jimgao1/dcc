from web3 import Web3, HTTPProvider
import json

class DCCInterface:
    def __init__(self, contract_id):
        provider = HTTPProvider('http://10.8.3.1:8545')
        self.web3 = Web3([provider])

        # 0x7eb00cdb92a9e87dab53f64b23936718d5507c35
        contract_address = Web3.toChecksumAddress(contract_id.lower())
        contract_abi = json.loads(open('files/abi_compact.json', 'r').read())

        self.contract = self.web3.eth.contract(address=contract_address, abi=contract_abi)

        print("Contract with address {} intialized".format(self.contract.address))

    def get_owner(self):
        return self.contract.functions.owner().call()

    def get_in_progress(self):
        return self.contract.functions.inProgress().call()

    def get_price(self):
        return self.contract.functions.price().call()

    def get_src_code(self):
        return self.contract.functions.srcCode().call()

    def submit_result(self, encodedBinary, binHash):
        pass
    
