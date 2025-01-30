from flask import Flask, request, session, render_template, redirect, url_for
from flask_socketio import SocketIO, Namespace, send, emit, join_room, leave_room
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
            break
    return code

@app.route('/', methods=['GET', 'POST'])
def index():
    session.clear()
    print(rooms)
    if request.method == 'POST':
        username = request.form.get('username')
        action = request.form.get('action')

        if not username or username.strip() == "":
            context = { "err": True, "msg": "Enter a valid username" }
            return render_template('index.html', ctx=context)
        if action == "Create Room":
            room = generate_code()
            rooms[room] = {"players": []}
            session["room"] = room
            session["name"] = username
            return redirect(url_for('lobby'))
        elif action == "Join Room":
            code = request.form.get('join-code')
            if code in rooms:
                session["room"] = code
                session["name"] = username
                return redirect(url_for('lobby'))
            else: 
                context = { "err": True, "msg": "Room does not exist" }
                return render_template('index.html', ctx=context)
    context = { "err": False, "msg": "" }
    return render_template('index.html', ctx=context)

@app.route('/lobby', methods=['GET', 'POST'])
def lobby():
    room = session.get("room")
    name = session.get("name")
    print(room)
    if room is None or session.get("name") is None or room not in rooms:
        return redirect(url_for("index"))
    
    if request.method == "POST":
        action = request.form.get('action')

        if action == 'leave': 
            return redirect(url_for('index'))
        elif action == 'start':
            return redirect(url_for('game'))
    
    context={ "room": room, "name": name }
    print(session.get("room"), session.get("name"))
    return render_template('lobby.html', ctx=context)

@app.route('/game', methods=['GET', 'POST'])
def game():
    return render_template('game.html')

class LobbyNamespace(Namespace):
    def on_connect(self):
        room = session.get("room")
        name = session.get("name")

        if room and name:
            join_room(room)
            rooms[room]["players"].append(name)
            socketio.emit("user_change", rooms[room], to=room)
        
        print(f"User {name} joined room {room}")

    def on_disconnect(self, reason):
        room = session.get("room")
        name = session.get("name")

        if room and name:
            leave_room(room)
            rooms[room]["players"].remove(name)
            if len(rooms[room]["players"]) == 0:
                del rooms[room]
            else:
                socketio.emit("user_change", rooms[room], to=room)

        print(f"User {name} left room {room}")

    def on_join_room(self, data):
        room = data.get("room")
        name = data.get("name")

        print(f"Room: {room} and Name: {name}")

class GameNamespace(Namespace):
    def on_connect(self):
        pass

    def on_disconnect(self, reason):
        pass

    def on_my_event(self, data):
        emit('my_response', data)

socketio.on_namespace(LobbyNamespace('/lobby'))
socketio.on_namespace(GameNamespace('/game'))

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0')