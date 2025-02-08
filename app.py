from flask import Flask, request, session, render_template, redirect, url_for
from flask_socketio import SocketIO, Namespace, send, emit, join_room, leave_room, disconnect
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
    room = session.get("room")
    name = session.get("name")
    if room in rooms and name in rooms[room]["players"]:
        rooms[room]["players"].remove(name)
        if len(rooms[room]["players"]) == 0:
            del rooms[room]
    session.clear()
    if request.method == 'POST':
        username = request.form.get('username')
        action = request.form.get('action')

        if not username or username.strip() == "":
            context = { "err": True, "msg": "Enter a valid username" }
            return render_template('index.html', ctx=context)
        if action == "Create Room":
            room = generate_code()
            rooms[room]={
                            "players": [], 
                            "game": {
                                        "started": False
                                    }
                        }
            session["room"] = room
            session["name"] = username
            rooms[room]["players"].append({"username": username})
            print(rooms[room]["players"])
            return redirect(url_for('lobby'))
        elif action == "Join Room":
            code = request.form.get('join-code')
            if code in rooms and rooms[code]["game"]["started"]:
                context = { "err": True, "msg": "Game Started" }
                return render_template('index.html', ctx=context)
            if code in rooms:
                session["room"] = code
                session["name"] = username
                rooms[code]["players"].append({"username": username})
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
    if room is None or name is None or room not in rooms:
        return redirect(url_for("index"))
    
    if request.method == "POST":
        action = request.form.get('action')

        if action == 'leave': 
            return redirect(url_for('index'))
    
    context={ "room": room }
    print(context)
    return render_template('lobby.html', ctx=context)

@app.route('/game', methods=['GET', 'POST'])
def game():
    room = session.get("room")
    name = session.get("name")
    if room is None or name is None or room not in rooms:
        return redirect(url_for("index"))
    return render_template('game.html', ctx=rooms[room])

class LobbyNamespace(Namespace):
    def on_connect(self):
        room = session.get("room")
        name = session.get("name")

        print(f"User {name} joined room {room}")
        join_room(room)
        socketio.emit("user_change", rooms[room], namespace='/lobby', to=room)
        

    def on_disconnect(self, reason):
        room = session.get("room")
        name = session.get("name")

        print(f"User {name} left room {room}")
        leave_room(room)
        if room in rooms and rooms[room]["players"]:
            socketio.emit("user_change", rooms[room], namespace='/lobby', to=room)
        
    def on_start_game(self, data):
        room = session.get("room")
        
        if room in rooms and rooms[room]["players"]:
            socketio.emit('game_start', {'message': 'Game is starting!'}, namespace='/lobby', to=room)
            rooms[room]["game"]["started"] = True

class GameNamespace(Namespace):
    def on_connect(self):
        room = session.get("room")
        name = session.get("name")
        sid = request.sid

        if room in rooms:
            for player in rooms[room]["players"]:
                if player["username"] == name:
                    player["sid"] = sid
                    print(f"User {name} SID added: {sid}")
                    break
        else:
            disconnect()

    def on_disconnect(self, reason):
        print("Game Disconnect")

    def on_submit_bid(self, data):
        name = session.get("name")
        print(f"{name} submit data: {data}")


socketio.on_namespace(LobbyNamespace('/lobby'))
socketio.on_namespace(GameNamespace('/game'))

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0')