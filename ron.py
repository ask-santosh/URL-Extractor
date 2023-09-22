from flask import Flask, render_template
from flask_socketio import SocketIO, emit, disconnect

import subprocess

async_mode = None

app = Flask(__name__)

socket_ = SocketIO(app, async_mode=async_mode)

@app.route('/')
def index():
    return render_template('index.html', sync_mode=socket_.async_mode)

@socket_.on('do_task', namespace='/test')
def run_lengthy_task(data):
    try:
        proc = subprocess.Popen(['ping', '127.0.0.1'], bufsize=0, stdout=subprocess.PIPE)
        for line in iter(proc.stdout.readline, b''):
            emit('task_update', { 'data': line.decode('utf-8')[:-1] })
        proc.stdout.close()
        proc.wait()
        result = proc.returncode
        emit('task_done', {'result': result})
        disconnect()
    except Exception as ex:
        print(ex)

if __name__ == '__main__':
    socket_.run(app, host='0.0.0.0', port=80, debug=True, allow_unsafe_werkzeug=True)
