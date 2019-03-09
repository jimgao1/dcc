from flask import Flask

app = Flask(__name__)

@app.route('/')
def default():
    return 'You should not be here.'

@app.route('/jobs')
def get_jobs():
    return 'Placeholder'

if __name__ == '__main__':
    app.run()
