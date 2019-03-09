from contracts import DCCInterface
from web3 import Web3, HTTPProvider

import io
import requests
import time
import json
import ipfsapi
import hashlib

private_key = 'da8328e960737b1a47a7f6a8bc6575809c5c9c5cbbb9bc11c24f58024b018620'
w3 = Web3([HTTPProvider('http://10.8.3.1:8545')])
acct = w3.eth.account.privateKeyToAccount(private_key)
w3.eth.defaultAccount = acct.address

while True:
    # Sleep
    time.sleep(5)

    # Get jobs
    r = requests.get('http://localhost:5000/api/jobs')
    lst = json.loads(r.text.replace('\'', '"'))
    
    if len(lst) == 0:
        continue

    # Get first available job
    contract_addr = lst[0]
    iface = DCCInterface(w3, contract_addr)

    print (iface)

    # Get job resources
    api = ipfsapi.connect('10.8.3.1', 5001)
    preprocess = api.cat(iface.get_src_code())

    # Do job
    postprocess = preprocess.upper()

    m = hashlib.sha256()
    m.update(postprocess)
    post_file_hash = int.from_bytes(m.digest(), byteorder='big')

    res = api.block_put(io.BytesIO(postprocess))
    post_ipfs_hash = res['Hash']

    print("file_hash:", post_file_hash, "ipfs:", post_ipfs_hash)
    
    iface.submit_result(post_ipfs_hash, post_file_hash)

