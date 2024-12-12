import os
import json
import socket
import threading
from flask import Flask, render_template, request, send_from_directory, abort
from datetime import datetime


STORAGE_DIR = "storage"
DATA_FILE = os.path.join(STORAGE_DIR, "data.json")

if not os.path.exists(STORAGE_DIR):
    os.makedirs(STORAGE_DIR)

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({}, f)


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/message', methods=['GET', 'POST'])
def message():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        message = request.form.get('message', '').strip()

        if username and message:
            
            data = json.dumps({"username": username, "message": message}).encode('utf-8')
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.sendto(data, ("127.0.0.1", 5000))

            return "Message sent successfully!"
        else:
            return "Invalid input, please try again."

    return render_template('message.html')


@app.route('/static/<path:path>')
def static_files(path):
    return send_from_directory('static', path)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html'), 404


def start_socket_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(("127.0.0.1", 5000))

    while True:
        data, _ = server_socket.recvfrom(4096)
        message_data = json.loads(data.decode('utf-8'))
        timestamp = datetime.now().isoformat()

        
        with open(DATA_FILE, 'r+') as f:
            existing_data = json.load(f)
            existing_data[timestamp] = message_data
            f.seek(0)
            json.dump(existing_data, f, indent=4)


if __name__ == '__main__':
    threading.Thread(target=start_socket_server, daemon=True).start()
    app.run(host='0.0.0.0', port=3000)