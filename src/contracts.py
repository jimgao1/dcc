from web3 import Web3, HTTPProvider
import json
import time

contract_abi = json.loads(open('files/abi_compact.json', 'r').read())
contract_code = open('files/master.bin', 'r').read()

def create_contract(web3: Web3, src, price, clients):
    contract = web3.eth.contract(abi = contract_abi, bytecode = contract_code)
    tx_hash = contract.constructor(src, clients).transact({
        'value': price,
    })
    tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)
    return DCCInterface(web3, tx_receipt.contractAddress)

class DCCInterface:
    def __init__(self, web3: Web3, contract_id):
        self.web3 = web3

        # 0x7eb00cdb92a9e87dab53f64b23936718d5507c35
        self.contract_address = Web3.toChecksumAddress(contract_id.lower())

        self.contract = self.web3.eth.contract(address=self.contract_address, abi=contract_abi)

        print("Contract with address {} intialized".format(self.contract.address))

    def __str__(self):
        return str({
            'addr': self.contract_address,
            'owner': self.get_owner(),
            'in_progress': self.get_in_progress(),
            'price': self.get_price(),
            'src_code': self.get_src_code()
        })

    def get_owner(self):
        return self.contract.functions.owner().call()

    def get_in_progress(self):
        return self.contract.functions.inProgress().call()

    def get_price(self):
        return self.contract.functions.price().call()

    def get_src_code(self):
        return self.contract.functions.srcCode().call()

    def get_slaves(self):
        return self.contract.functions.getSlaveAddresses().call()

    def get_slave(self, slaveHash):
        return self.contract.functions.getSlave(slaveHash).call()

    def submit_result(self, encodedBinary, binHash):
        self.contract.functions.submit(binHash, encodedBinary).transact()
    
