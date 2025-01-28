from flask import Flask, request, session, render_template, redirect, url_for
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

@app.route('/', methods=['GET', 'POST'])
def index():
    session.clear()
    if request.method == 'POST':
        username = request.form.get('username')
        action = request.form.get('action')

        if not username or username.strip() == "":
            context = { "err": True, "msg": "Enter a valid username" }
            return render_template('index.html', ctx=context)
        if action == "Create Room":
            room = generate_code()
            rooms[room] = {"total_players": 0, "players": []}
            session["room"] = room
            session["name"] = username
            return redirect(url_for('lobby', code=room))
        elif action == "Join Room":
            code = request.form.get('join-code')
            if code in rooms:
                session["room"] = code
                session["name"] = username
                return redirect(url_for('lobby', code=code))
            else: 
                context = { "err": True, "msg": "Room does not exist" }
                return render_template('index.html', ctx=context)
    context = { "err": False, "msg": "" }
    return render_template('index.html', ctx=context)

@app.route('/lobby/<code>', methods=['GET', 'POST'])
def lobby(code):
    room = session.get("room")
    if room is None or session.get("name") is None or room not in rooms:
        return redirect(url_for("index"))
    
    if request.method == "POST":
        return redirect(url_for('index'))
    
    context={
                "code": code
            }
    return render_template('lobby.html', ctx=context)

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