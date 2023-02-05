from flask import Flask, render_template, request, redirect, url_for, session
import secrets
import os
import platform
import subprocess
import eventlet
from flask_socketio import SocketIO, emit

print("Press Ctrl + C to quit")

app = Flask(__name__)

my_secret_key = secrets.token_urlsafe(16)
app.secret_key = my_secret_key

socketio = SocketIO(app)

messages = []

@app.route('/')
def index():
    if 'username' not in session:
        return render_template('set_username.html')
    else:
        return render_template('index.html', messages=messages)

@app.route('/set_username', methods=['POST'])
def set_username():
    session['username'] = request.form['username']
    return redirect(url_for('index'))

@app.route('/messages')
def view_messages():
    return render_template('messages.html', messages=messages)

@app.route('/send', methods=['POST'])
def send():
    message = request.form['message']
    username = session['username']
    messages.append(f"{username}: {message}")
    socketio.emit('new_message', {'username': username, 'message': message})
    return redirect(url_for('index'))

def get_ip_address():
    system = platform.system()
    if system == 'Windows':
        process = subprocess.Popen(['ipconfig'], stdout=subprocess.PIPE)
        stdout, _ = process.communicate()
        output = stdout.decode('utf-8')
        lines = output.split('\n')
        for line in lines:
            if 'IPv4' in line:
                ip = line.split(':')[1].strip()
                return ip
    elif system == 'Linux':
        process = subprocess.Popen(['hostname', '-I'], stdout=subprocess.PIPE)
        stdout, _ = process.communicate()
        ip = stdout.decode('utf-8').strip()
        return ip
    elif system == 'Darwin':
        process = subprocess.Popen(['ifconfig'], stdout=subprocess.PIPE)
        stdout, _ = process.communicate()
        output = stdout.decode('utf-8')
        lines = output.split('\n')
        for line in lines:
            if 'inet ' in line and '127.0.0.1' not in line:
                ip = line.split()[1]
                return ip
    else:
        return None

ip = get_ip_address()
port = 5000

print(f"App running on {ip}:{port}")

if __name__ == '__main__':
    socketio.run(app, host=ip, port=port)
