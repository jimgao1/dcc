from flask import Flask, request
from contracts import DCCInterface

import json
import _thread
import time

app = Flask(__name__)
jobs = []

def thread_prune_entries():
    global jobs
    while True:
        print ("Pruning entires!")
        new_jobs = []
        for j in jobs:
            try:
                iface = DCCInterface(j)
                new_jobs.append(j)
            except:
                pass

        jobs = new_jobs

        time.sleep(5)

@app.route('/')
def default():
    return 'You should not be here.'

@app.route('/jobs')
def get_jobs():
    return str(jobs)

@app.route('/addjob', methods=['POST'])
def add_job():
    try:
        contract_id = request.data.decode('utf-8')

        if contract_id in jobs:
            raise Exception

        jobs.append(contract_id)
        return 'ok'
    except:
        return 'fail'

if __name__ == '__main__':
    _thread.start_new_thread(thread_prune_entries, ())
    app.run()
