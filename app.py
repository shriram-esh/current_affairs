from flask import Flask, request, session, render_template, redirect, url_for
from flask_socketio import SocketIO, Namespace, send, emit, join_room, leave_room, disconnect
from functools import wraps
from dotenv import load_dotenv
from graph import create_graph
from urllib.parse import parse_qs
import numpy as np
from scipy.optimize import linprog
import random
import os
import random
import string
from gameplay import *

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app, cors_allowed_origins='*', manage_session=False)

rooms = {}

def generate_code():
    while (True):
        code = ''.join(random.choices(string.ascii_uppercase, k=4))
        if code not in rooms:
            break
    return code

def linprog_to_graph(in_data, in_linprog, demand, marketPrice):
    cur_width = 0
    xList = []
    widthBar = []
    barHeight = []
    colors = []
    players = []
    for index, p in enumerate(in_data):
        if in_linprog[index] > 0 and in_linprog[index] < p["bidQuantity"]:
            # Line intersects bar
            barHeight.append(p["bidPrice"])
            xList.append(in_linprog[index] / 2 + cur_width)
            widthBar.append(in_linprog[index])
            colors.append(f'rgba({p["color"][0]}, {p["color"][1]}, {p["color"][2]}, 1)')
            players.append(p["player"].name)
            cur_width += in_linprog[index]
            barHeight.append(p["bidPrice"])
            xList.append(((p["bidQuantity"] - in_linprog[index]) / 2 + cur_width))
            widthBar.append(p["bidQuantity"] - in_linprog[index])
            colors.append(f'rgba({p["color"][0]}, {p["color"][1]}, {p["color"][2]}, 0.25)')
            players.append(p["player"].name)
            cur_width += p["bidQuantity"] - in_linprog[index]
        else:
            barHeight.append(p["bidPrice"])
            xList.append(p["bidQuantity"] / 2 + cur_width)
            widthBar.append(p["bidQuantity"])
            players.append(p["player"].name)
            cur_width += p["bidQuantity"]
            if in_linprog[index] == 0:
                colors.append(f'rgba({p["color"][0]}, {p["color"][1]}, {p["color"][2]}, 0.25)')
            else:
                colors.append(f'rgba({p["color"][0]}, {p["color"][1]}, {p["color"][2]}, 1)')
    return  {
                "barHeight": barHeight,
                "xList": xList,
                "widthBar": widthBar,
                "colors": colors,
                "demand": demand,
                "marketPrice": marketPrice,
                "players": players
            }

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        room = session.get("room")
        name = session.get("name")
        print(f"Room: {room} Name: {name}")
        if room is None or name is None or room not in rooms:  # Check if user is in session
            print("'index' check")
            if request.endpoint != "index":
                print("Redirect to 'index'")
                return redirect(url_for("index"))  # Redirect to login if not logged in
        elif not rooms[room]["game"]["started"]: # Check if game is still in lobby
            print("'lobby' check")
            if request.endpoint != "lobby":
                print("Redirect to 'lobby'")
                return redirect(url_for("lobby"))
        elif rooms[room]["game"]["started"]:
            print("'game' check")
            if request.endpoint != "game":
                print("Redirect to 'game'")
                return redirect(url_for("game"))
    
        return f(*args, **kwargs)  # Otherwise, proceed to the game
    return decorated_function

@app.route("/logout")
def logout():
    session.pop("name", None)  
    return redirect(url_for("index"))

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    room = session.get("room")
    name = session.get("name")

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
                            "dataList": [], 
                            "game": {
                                        "started": False,
                                        "hasDemand": False,
                                        "curDemand": 0
                                    }
                        }
            session["room"] = room
            session["name"] = username

            return redirect(url_for('lobby'))
        elif action == "Join Room":
            code = request.form.get('join-code')
            if code in rooms and rooms[code]["game"]["started"]:
                context = { "err": True, "msg": "Game Started" }
                return render_template('index.html', ctx=context)
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
@login_required
def lobby():
    room = session.get("room")
    name = session.get("name")
    if room is None or name is None or room not in rooms:
        return redirect(url_for("index"))
    
    if request.method == "POST":
        action = request.form.get('action')

        if action == 'leave': 
            return redirect(url_for('logout'))
    
    context={ "room": room }
    return render_template('lobby.html', ctx=context)

@app.route('/game', methods=['GET', 'POST'])
@login_required
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

        if room in rooms and name:
            print(f"User {name} joined room {room}")
            print(rooms[room])
            join_room(room)
            rooms[room]["players"].append(  
                                            {
                                                "username": name,
                                            }
                                        )
            socketio.emit("user_change", rooms[room], namespace='/lobby', to=room)
        else:
            socketio.emit("player_left", {'msg': "gone"}, namespace='/lobby', to=request.sid)

    def on_disconnect(self, reason):
        room = session.get("room")
        name = session.get("name")

        print(f"User {name} left room {room}")
        leave_room(room)
        
        if rooms[room]["game"]["started"]:
            return

        if room in rooms:
            for player in rooms[room]["players"]:
                if player["username"] == name:
                    rooms[room]["players"].remove(player)
                    break
        
        if len(rooms[room]["players"]) == 0:
            print(f"Delete room {room}")
            del rooms[room]

        if room in rooms and rooms[room]["players"]:
            socketio.emit("user_change", rooms[room], namespace='/lobby', to=room)

    def on_start_game(self, data):
        room = session.get("room")

        # randomize quantity and portfolio for everyone
        rooms[room]["dataList"] = define_players(usable_assets, rooms[room]["players"])
        
        if room in rooms and rooms[room]["players"]:
            socketio.emit('game_start', {'message': 'Game is starting!'}, namespace='/lobby', to=room)
            rooms[room]["game"]["started"] = True

class GameNamespace(Namespace):
    def on_connect(self):
        room = session.get("room")
        name = session.get("name")
        sid = request.sid

        join_room(room)

        print(f"User: {name} Room: {room} SID: {sid}")

        if room in rooms:
            for player in rooms[room]["dataList"]:
                if player.name == name:
                    player.sid = sid
                    print(f"User {name} SID updated: {sid}")
                    break
        else:
            disconnect()

    def on_disconnect(self, reason):
        room = session.get("room")
        leave_room(room)
        print("Game Disconnect")
    
    def on_get_stats(self):
        room = session.get("room")
        name = session.get("name")

        for player in rooms[room]["dataList"]:
            if player.name == name:
                data = {
                    "asset": assets[player.bids[0].asset][0],
                    "units": player.bids[0].units,
                    "generation": assets[player.bids[0].asset][1]
                }
                socketio.emit('send_stats', data, namespace='/game', to=player.sid)
                print(f"Sent Stats {data} to {player.name}")
                break

    def on_submit_bid(self, data):
        room = session.get("room")
        name = session.get("name")
        if room not in rooms:
            disconnect()

        if not rooms[room]["game"]["hasDemand"]:
            rooms[room]["game"]["curDemand"] = 4 # random.randint(100, 120) # randomize the demand
            rooms[room]["game"]["hasDemand"] = True

        parsed_data = parse_qs(data.get('data', ''))
        parsed_data_clean = {}
        print(parsed_data)

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
        
        # Have They Already Placed a Bid
        for player in rooms[room]["dataList"]:
            if player.name == name and player.hasBid:
                socketio.emit('bid_status', {'message': 'Already placed bid. Wait till next round!'}, namespace='/game', to=player.sid)
                return

        # Error Check data
        for player in rooms[room]["dataList"]:
            if player.name != name:
                continue

            if 'quantity' not in parsed_data:
                socketio.emit('bid_status', {'message': f'Enter a Quantity!'}, namespace='/game', to=player.sid)
                return
        
            if 'price' not in parsed_data:
                socketio.emit('bid_status', {'message': f'Enter a Price!'}, namespace='/game', to=player.sid)
                return

            # Check price is valid and dosen't exceed market price
            if (parsed_data_clean["price"] < 0 or parsed_data_clean["price"] > market_cap):
                socketio.emit('bid_status', {'message': 'Enter a different price (ensure it is non-negative number below the market cap)'}, namespace='/game', to=player.sid)
                return

            if (parsed_data_clean["quantity"] < 0 or parsed_data_clean["quantity"] > player.bids[0].units):
                socketio.emit('bid_status', {'message': f'Enter a different quantity (ensure it is non-negative number below the number of units you have ({player.bids[0].units})'}, namespace='/game', to=player.sid)
                return
            player.bids[0].price = float(parsed_data_clean["price"])
            player.bids[0].quantity = float(parsed_data_clean["quantity"])
            player.hasBid = True
            
            socketio.emit('bid_status', {'message': 'Bid successful!'}, namespace='/game', to=player.sid)
 
        print(f"{name} submit data: {parsed_data_clean}")

        # Check if everyone has voted
        if all(player.hasBid for player in rooms[room]["dataList"]):

            all_bids = []
            for player in rooms[room]["dataList"]:
                for bid in player.bids:
                    all_bids.append({"player": player, "data": bid, "bidPrice": bid.price, "bidQuantity": bid.quantity, "color": player.color})
            sorted_bids = sorted(all_bids, key=lambda x: x["bidPrice"])

            prices = []
            quantities = []
            for bid in sorted_bids:
                print(bid)
                prices.append(bid["data"].price)
                quantities.append(bid["data"].quantity)
            demand = rooms[room]["game"]["curDemand"]

            c = prices #prices
            u = quantities #quantities of each good
            b_eq = [demand, 0]

            #l = [0]*len(c)
            A_eq = [[1]*len(c), [0]*len(c)]
            bounds = []
            for upper_bound in u:
                bounds.append((0, upper_bound))

            #define the quantities cleared and market price  USING MAGIC
            if sum(u) >= demand:
                res = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=bounds)
                print(f"The marginal returned from LinProg: {res.eqlin['marginals']}")
                print(f"The vector x returned from LinProg{res.x}\n\n")
                market_price = res.eqlin["marginals"][0] # What happens if supply dosen't meet demand
                x = res.x
            else:
                market_price = max(c)
                x = u

            graphData = linprog_to_graph(sorted_bids, x, demand, market_price)

            player_profits = []
            for index, bid in enumerate(sorted_bids):
                bid["player"].profit += (market_price - assets[bid["data"].asset][1]) * x[index]
                player_profits.append({"player": bid["player"].name, "total": bid["player"].profit})
            print(player_profits)
            data =  {
                        "graphData": graphData,
                        "playerProfits": player_profits
                    }
            
            socketio.emit('round_over', data, namespace='/game', to=room)
            for player in rooms[room]["dataList"]:
                player.hasBid = False
            rooms[room]["game"]["hasDemand"] = False

socketio.on_namespace(LobbyNamespace('/lobby'))
socketio.on_namespace(GameNamespace('/game'))

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)