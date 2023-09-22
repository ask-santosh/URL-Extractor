import json
import os
import time
import uuid

from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, disconnect
import pandas as pd
from werkzeug.utils import secure_filename

import helpers

async_mode = None

app = Flask(__name__)
app.secret_key = b'SecretKey to be added later on'
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), "uploads")
GEN_FOLDER = os.path.join(os.getcwd(), "static", "generated")

socket_ = SocketIO(app, async_mode=async_mode)


@app.route('/')
def index():
    return render_template('home.html', sync_mode=socket_.async_mode)


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    file = request.files['uploadFile']
    file_id = str(uuid.uuid4()).replace("-", "") + "." + file.filename.split(".")[-1]
    file_id = secure_filename(file_id)
    if file:
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file_id))

        return json.dumps({'page': "/task", 'file_id': file_id}), 200, {'ContentType': 'application/json'}
    return render_template('home.html', sync_mode=socket_.async_mode)


@app.route('/task', methods=['GET'])
def task_page():
    file_id = request.args.get("file_name")
    if file_id:
        return render_template('main.html', sync_mode=socket_.async_mode, file_id=file_id)


@socket_.on('do_task', namespace='/test')
def run_lengthy_task(data):
    millisec = int(round(time.time() * 1000))
    file_name = data.get("file_id", None)
    if not file_name:
        emit('task_done', {'result': "Invalid file name"})
        disconnect()

    df = None
    try:
        if file_name.split(".")[-1] == "csv":
            df = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], file_name), header=None)
        elif file_name.split(".")[-1] in ["xlsx", "xls"]:
            df = pd.read_excel(os.path.join(app.config['UPLOAD_FOLDER'], file_name), header=None, engine="openpyxl")
        else:
            emit('task_done', {'result': "Invalid file format"})
            disconnect()

    except FileNotFoundError:
        emit('task_done', {'result': "file not found"})
        disconnect()

    except Exception as ex:
        print(ex)

    if df.empty:
        emit('task_done', {'result': "no data not found"})
        disconnect()

    ctr = 0
    suc_ctr = 0
    urls = []
    remarks = []

    for url in df[0]:
        ctr += 1
        url = helpers.preprocess_link(url)["url"]
        res = helpers.without_selenium(url)
        extracted_links = res.get("extracted_links", None)
        if res.get("err_msg", None) or not extracted_links:
            res = helpers.with_selenium(url)

        urls.append(url)

        if not extracted_links:
            if not res:
                msg = "Some high level error"
            else:
                if res.get('status_code', None) == 200:
                    msg = f"Status Code: {res.get('status_code', None)} <br/> Error: No facebook link found"
                    remarks.append(msg.replace("<br/>", "\\n"))
                else:
                    msg = f"Status Code: {res.get('status_code', None)} <br/> Error: {res.get('err_msg', None)}"
                    remarks.append(msg.replace("<br/>", "\\n"))
        else:
            msg = ""
            for ex_link in extracted_links:
                msg = msg + str(ex_link) + " <br/> "
            suc_ctr += 1
            remarks.append(msg.replace("<br/>", "\\n"))

        emit('task_update', {'url': url, 'data': msg})
        time.sleep(0.1)

    suc_rate = round((suc_ctr/ctr)*100, 2)

    out_df = pd.DataFrame({'URL': urls, 'Remarks': remarks})
    out_key = "out_" + str(uuid.uuid4())
    out_file = os.path.join(GEN_FOLDER, out_key+".xlsx")
    out_df.to_excel(out_file, index=False)

    emit('task_done', {'result': f"Extraction Rate: {suc_rate}%", "out_key": out_key})

    disconnect()
    print("Time taken in ms: ", int(round(time.time() * 1000)) - millisec)


if __name__ == '__main__':
    socket_.run(app, host='0.0.0.0', port=80, debug=True, allow_unsafe_werkzeug=True)
