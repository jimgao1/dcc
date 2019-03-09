from contracts import DCCInterface
from web3 import Web3, HTTPProvider

import io
import requests
import time
import json
import ipfsapi
import hashlib
import tarfile
import docker

private_key = 'da8328e960737b1a47a7f6a8bc6575809c5c9c5cbbb9bc11c24f58024b018620'
w3 = Web3([HTTPProvider('http://10.8.3.1:8545')])
acct = w3.eth.account.privateKeyToAccount(private_key)
w3.eth.defaultAccount = acct.address

tasks_done = []
docker_client = docker.from_env()


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
    if contract_addr in tasks_done:
        continue

    tasks_done.append(contract_addr)

    iface = DCCInterface(w3, contract_addr)

    print (iface)

    # Get job resources
    api = ipfsapi.connect('10.8.3.1', 5001)
    build_archive = io.BytesIO(api.block_get(iface.get_src_code()))

    tar = tarfile.open(fileobj=build_archive)
    build_folder = tar.extractall("/tmp/dcc-build")
    tar.close()

    config = json.loads(open("/tmp/dcc-build/dcc-config.json", "r").read())
    docker_client.containers.run(config['image'], config['exec'], volumes={
        '/tmp/dcc-build': { 'bind': '/src', 'mode': 'rw' },
        }, 'working_dir'="/src")
    docker_client.containers.prune()

    postprocess = open("/tmp/dcc-build/" + config['binary'], 'r').read()

    m = hashlib.sha256()
    m.update(postprocess)
    post_file_hash = int.from_bytes(m.digest(), byteorder='big')

    res = api.block_put(io.BytesIO(postprocess))
    post_ipfs_hash = res['Key']

    print("file_hash:", post_file_hash, "ipfs:", post_ipfs_hash)
    
    iface.submit_result(post_ipfs_hash, post_file_hash)

