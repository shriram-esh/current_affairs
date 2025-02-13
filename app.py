from flask import Flask, request, session, render_template, redirect, url_for
from flask_socketio import SocketIO, Namespace, send, emit, join_room, leave_room, disconnect
from dotenv import load_dotenv
from optimize import MarketRound
from urllib.parse import parse_qs
import numpy as np
from scipy.optimize import linprog
import random
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
                                        "started": False,
                                        "hasDemand": False,
                                        "curDemand": 0,
                                        "pastRounds": []
                                    }
                        }
            session["room"] = room
            session["name"] = username
            rooms[room]["players"].append(  
                                            {
                                                "username": username,
                                                "bidPrice": 0,
                                                "bidQuantity": 0,
                                                "hasBid": False
                                            }
                                        )
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
                rooms[code]["players"].append(  
                                                {
                                                    "username": username,
                                                    "bidPrice": 0,
                                                    "bidQuantity": 0,
                                                    "hasBid": False
                                                }
                                            )
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

        # randomize quantity and portfolio for everyone
        
        if room in rooms and rooms[room]["players"]:
            socketio.emit('game_start', {'message': 'Game is starting!'}, namespace='/lobby', to=room)
            rooms[room]["game"]["started"] = True

class GameNamespace(Namespace):
    def on_connect(self):
        room = session.get("room")
        name = session.get("name")
        sid = request.sid

        join_room(room)

        if room in rooms:
            for player in rooms[room]["players"]:
                if player["username"] == name:
                    player["sid"] = sid
                    print(f"User {name} SID updated: {sid}")
                    break
        else:
            disconnect()

    def on_disconnect(self, reason):
        room = session.get("room")
        leave_room(room)
        print("Game Disconnect")

    def on_submit_bid(self, data):
        room = session.get("room")
        name = session.get("name")

        if not rooms[room]["game"]["hasDemand"]:
            rooms[room]["game"]["curDemand"] = random.randint(100, 120)
            rooms[room]["game"]["hasDemand"] = True

        parsed_data = parse_qs(data.get('data', ''))
        parsed_data_clean = {}
        for key, values in parsed_data.items():
            try:
                # Try converting the value to an int
                parsed_data_clean[key] = int(values[0])
            except ValueError:
                try:
                    # If that fails, try converting the value to a float
                    parsed_data_clean[key] = float(values[0])
                except ValueError:
                    # If both conversions fail, keep it as original type
                    parsed_data_clean[key] = values[0]

        if room in rooms:
            for player in rooms[room]["players"]:
                if player["username"] == name and not player["hasBid"]:
                    player["bidPrice"] = parsed_data_clean["price"]
                    player["bidQuantity"] = parsed_data_clean["quantity"]
                    player["hasBid"] = True
                    socketio.emit('bid_status', {'message': 'Bid successful!'}, namespace='/game', to=player["sid"])
                elif player["hasBid"]:
                    socketio.emit('bid_status', {'message': 'Already placed bid. Wait till next round!'}, namespace='/game', to=player["sid"])
        else:
            disconnect()
        print(f"{name} submit data: {parsed_data_clean}")

        # Check if everyone has voted
        if all(player["hasBid"] for player in rooms[room]["players"]):
            bids = [player["bidPrice"] for player in rooms[room]["players"]]
            quantity = [player["bidQuantity"] for player in rooms[room]["players"]]
            demand = rooms[room]["game"]["curDemand"]

            try:
                marketOutcome = MarketRound(bids, quantity, demand)
            except (TypeError, ValueError) as e:
                print(f"Error: {e}")
            result = marketOutcome.get_result()

            c = bids #prices
            u = quantity #quantities of each good
            b_eq = [demand, 0]
            

            #l = [0]*len(c)
            A_eq = [[1]*len(c), [0]*len(c)]
            bounds = []
            for upper_bound in u:
                bounds.append((0, upper_bound))

            #define the quantities cleared and market price  USING MAGIC
            res = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=bounds)
            print(f"The marginal returned from LinProg: {res.eqlin['marginals']}")
            market_price = res.eqlin["marginals"][0]
            print(f"The vector x returned from LinProg{res.x}\n\n")
            x = res.x

            player_prices = [
                {"bidQuantity": bid, "bidPrice": player["bidPrice"], "player": player["username"]} 
                for player, bid in zip(rooms[room]["players"], x)
            ]

            sorted_player_prices = sorted(player_prices, key=lambda item: item["bidPrice"])

            data =  {
                        "demandCutOff": demand,
                        "priceCutOff": market_price,
                        "bids": sorted_player_prices
                    }
            
            print(f"round over: \n{data}\n{room}")
            socketio.emit('round_over', data, namespace='/game', to=room)

socketio.on_namespace(LobbyNamespace('/lobby'))
socketio.on_namespace(GameNamespace('/game'))

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)