from flask import Flask

app = Flask(__name__)
jobs = []

@app.route('/')
def default():
    return 'You should not be here.'

@app.route('/jobs')
def get_jobs():
    return str(jobs)

if __name__ == '__main__':
    app.run()
