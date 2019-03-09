from flask import Flask, request
from contracts import DCCInterface

import json
import _thread
import time
import traceback

app = Flask(__name__)
jobs = []
jobs_details = []

def thread_prune_entries():
    global jobs
    global jobs_details
    while True:
        print ("Pruning entires!")
        new_jobs = []
        new_jobs_details = []
        for j in jobs:
            try:
                iface = DCCInterface(j)
                new_jobs_details.append({
                    'id': j,
                    'owner': iface.get_owner(),
                    'in_progress': 'Ongoing' if iface.get_in_progress() else 'Completed/Failed',
                    'price': iface.get_price()
                })

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
        return 'fail'

if __name__ == '__main__':
    _thread.start_new_thread(thread_prune_entries, ())
    app.run()
