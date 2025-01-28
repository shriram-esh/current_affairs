from flask import Flask, request, render_template, redirect, url_for
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from dotenv import load_dotenv
import os
import random
import string

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app, cors_allowed_origins='*')

rooms = {}

def generate_code():
    while (True):
        code = ''.join(random.choices(string.ascii_uppercase, k=4))
        if code not in rooms:
            rooms[code] = {"players": []}
            break
    return code

@app.route('/')
def index():
    context = { "err": False, "msg": "" }
    return render_template('index.html', ctx=context)

@app.route('/room_action', methods=['POST'])
def room_action():
    username = request.form.get('username')
    action = request.form.get('action')

    if not username or username.strip() == "":
        context = { "err": True, "msg": "Enter a valid username" }
        return render_template('index.html', ctx=context)

    if action == "Create Room":
        return redirect(url_for('lobby', code=generate_code()))
    
    elif action == "Join Room":
        code = request.form.get('join-code')
        if code in rooms:
            return redirect(url_for('lobby', code=code))
        else: 
            context = { "err": True, "msg": "Room does not exist" }
            return render_template('index.html', ctx=context)


@app.route('/lobby/<code>')
def lobby(code):
    return render_template('lobby.html', code=code)

@socketio.on('connect')
def user_connect(): 
    print("User Connected")

@socketio.on('disconnect')
def user_disconnect():
    print("User Disconnected")

@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    send(username + ' has entered the room.', to=room)

@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    send(username + ' has left the room.', to=room)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0')