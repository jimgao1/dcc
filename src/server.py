from flask import Flask, request
from contracts import DCCInterface
from web3 import Web3, HTTPProvider

import json
import _thread
import time
import traceback

app = Flask(__name__)
jobs = []
jobs_details = []
web3 = Web3([HTTPProvider("http://10.8.3.1:8545")])


def thread_prune_entries():
    global jobs
    global jobs_details
    while True:
        print ("Pruning entires!")
        new_jobs = []
        new_jobs_details = []
        for j in jobs:
            try:
                iface = DCCInterface(web3, j)
                new_jobs_details.append({
                    'id': j,
                    'owner': iface.get_owner(),
                    'in_progress': 'Ongoing' if iface.get_in_progress() else 'Completed/Failed',
                    'price': iface.get_price()
                })

                if iface.get_in_progress():
                    new_jobs.append(j)
            except Exception:
                traceback.print_exc()

        jobs = new_jobs
        jobs_details = new_jobs_details

        time.sleep(5)

@app.route('/')
def default():
    return str(jobs_details)

@app.route('/api/jobs')
def get_jobs():
    return str(jobs)

@app.route('/api/addjob', methods=['POST'])
def add_job():
    try:
        contract_id = request.data.decode('utf-8')

        if contract_id in jobs:
            raise Exception

        jobs.append(contract_id)
        return 'ok'
    except:
        traceback.print_exc()
        return 'fail'

if __name__ == '__main__':
    _thread.start_new_thread(thread_prune_entries, ())
    app.run(host="0.0.0.0")
