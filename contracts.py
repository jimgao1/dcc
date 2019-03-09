from web3 import Web3, HTTPProvider
import json

provider = HTTPProvider('http://10.8.3.1:8545')
web3 = Web3([provider])

print ('latest block', web3.eth.getBlock('latest'))

contract_address = Web3.toChecksumAddress('0x7eb00cdb92a9e87dab53f64b23936718d5507c35'.lower())
contract_abi = json.loads(open('files/abi_compact.json', 'r').read())

contract = web3.eth.contract(address=contract_address, abi=contract_abi)

print (contract)
