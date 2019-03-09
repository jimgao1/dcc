from contracts import DCCInterface
from web3 import Web3, HTTPProvider
from termcolor import colored, cprint

import io
import requests
import time
import json
import ipfsapi
import hashlib
import tarfile
import docker
import argparse

parser = argparse.ArgumentParser(description='DCC Client Program')
parser.add_argument('--w3provider', metavar='w3provider', type=str, default='http://100.65.198.211:8545')
parser.add_argument('--tracker', metavar='tracker', type=str, default='http://45.79.145.106:5000/')
parser.add_argument('--ipfs', metavar='ipfs', type=str, default='45.79.145.106')
parser.add_argument('--privkey', metavar='privkey', type=str, default='62e0dd6a206756c7fdd7c70d74579414ebe5edd0796556b27da9cf2293895f44')

args = parser.parse_args()
print (args)

# private_key = '62e0dd6a206756c7fdd7c70d74579414ebe5edd0796556b27da9cf2293895f44'
private_key = args.privkey
w3 = Web3([HTTPProvider(args.w3provider)])
acct = w3.eth.account.privateKeyToAccount(private_key)
w3.eth.defaultAccount = acct.address

tasks_done = []
docker_client = docker.from_env()

while True:
    # Sleep
    time.sleep(5)

    # Get jobs
    r = requests.get(args.tracker + 'api/jobs')
    lst = json.loads(r.text.replace('\'', '"'))
    
    if len(lst) == 0:
        continue

    # Get first available job
    contract_addr = lst[0]

    if contract_addr in tasks_done:
        continue
    tasks_done.append(contract_addr)

    cprint('NEW JOB: {}'.format(contract_addr), 'white', 'on_red', attrs=['bold'])
    iface = DCCInterface(w3, contract_addr)

    print (iface)

    # Get job resources
    api = ipfsapi.connect(args.ipfs, 5001)
    # build_archive = io.BytesIO(api.block_get(iface.get_src_code()))

    print("Downloading required files...")
    open('/tmp/dcc-build.tar.gz', 'wb').write(api.cat(iface.get_src_code()))

    # tar = tarfile.open(fileobj=build_archive, mode="r:gz")
    print ("Extracting files...")
    tar = tarfile.open('/tmp/dcc-build.tar.gz', mode="r:gz")
    build_folder = tar.extractall("/tmp/dcc-build")
    tar.close()

    print ("Executing task...")
    config = json.loads(open("/tmp/dcc-build/dcc-config.json", "r").read())
    docker_client.containers.run(config['image'], config['exec'], volumes={
        '/tmp/dcc-build': { 'bind': '/src', 'mode': 'rw' },
        }, working_dir="/src")
    docker_client.containers.prune()

    postprocess = open("/tmp/dcc-build/" + config['binary'], 'rb').read()

    m = hashlib.sha256()
    m.update(postprocess)
    post_file_hash = int.from_bytes(m.digest(), byteorder='big')

    res = api.block_put(io.BytesIO(postprocess))
    post_ipfs_hash = res['Key']

    print("Submitting hash...")
    iface.submit_result(post_ipfs_hash, post_file_hash)
    print("file_hash:", post_file_hash, "ipfs:", post_ipfs_hash)

    cprint('JOB COMPLETE', 'white', 'on_green', attrs=['bold'])
    print()
    

