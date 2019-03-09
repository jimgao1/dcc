import argparse
import ipfsapi
import requests
import time
import hash
import tarfile
from web3 import Web3, HTTPProvider

import contracts

def ipfs_connect(addr):
    host = addr.split(":")[0]
    port = addr.split(":")[1]

    return ipfsapi.connect(host, int(port))

def upload_folder(ipfs, folder):
    tar = tarfile.open('/tmp/dcc-build.tar.gz', 'w:gz')
    tar.add(folder, '')
    tar.close()
    res = ipfs.add('/tmp/dcc-build.tar.gz')
    return res['Hash']

def get_file(ipfs, hash):
    return ipfs.block_get(hash)

def main():
    parser = argparse.ArgumentParser(description="Distributed Compiler Collection")
    parser.add_argument('folder', metavar='FOLDER', type=str, help='folder to compile')
    parser.add_argument('private_key', metavar='PRIVATE_KEY', type=str, help='private key to use')
    parser.add_argument('price', metavar='PRICE', type=int, help='price in WEI')
    parser.add_argument('clients', metavar='CLIENTS', type=int, help='number of clients to distribute against')
    parser.add_argument('--ipfs', metavar='IPFS_ADDRESS', type=str, default='45.79.145.106:5001', help='ipfs address')
    parser.add_argument('--tracker', metavar='TRACKER_ADDRESS', type=str, default='http://45.79.145.106:5000', help='tracker address')
    parser.add_argument('--network', metavar='NETWORK', type=str, default='http://100.65.198.211:8545', help='ethereum network address')

    args = parser.parse_args()

    ipfs = ipfs_connect(args.ipfs)
    file_hash = upload_folder(ipfs, args.folder)
    print("uploaded to ipfs", file_hash)

    web3 = Web3([HTTPProvider(args.network)])
    acct = web3.eth.account.privateKeyToAccount(args.private_key)
    web3.eth.defaultAccount = acct.address

    contract = contracts.create_contract(web3, file_hash, args.price, args.clients)

    requests.post(args.tracker + "/api/addjob", data=contract.contract_address)
    filter = web3.eth.filter({'fromBlock':0, 'toBlock':'latest', 'address': contract.contract_address})
    while contract.get_in_progress():
        time.sleep(5)

    
    new_events = filter.get_new_entries()
    if len(new_events) != 1:
        raise Exception("multiple completed events")

    tx_receipt = web3.eth.getTransactionReceipt(new_events[0]['transactionHash'])
    completion = contract.contract.events.JobCompleted().processReceipt(tx_receipt)
    failed = contract.contract.events.JobFailed().processReceipt(tx_receipt)
    if len(completion) == 1 and len(failed) != 1:
        good_slaves_addr = completion[0]['args']['goodSlaves']
        slave_addrs = contract.get_slaves()
        good_slaves = []
        for slave_addr in good_slaves_addr:
            slave = contract.get_slave(slave_addrs[slave_addr])
            bin_data = get_file(ipfs, slave[1])

            if hash.hash(bin_data) == slave[0]:
                open('output', 'wb').write(bin_data)
                return
        
        print("there were no good binaries")
        return
    elif len(completion) != 1 and len(failed) == 1:
        print("there were large inconsistencies in compiling")
        return
    else:
        raise Exception("multiple completed events")


if __name__ == "__main__":
    main()

