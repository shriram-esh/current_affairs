from flask import Flask, request, session, render_template, redirect, url_for
from flask_socketio import SocketIO, Namespace, join_room, leave_room, disconnect
from functools import wraps
from dotenv import load_dotenv
from urllib.parse import parse_qs
from scipy.optimize import linprog
from model import *

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret_key"
socketio = SocketIO(app, cors_allowed_origins='*', manage_session=False)

room_manager = RoomManager()

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
        
        current_room = room_manager.get_room(room)
        if room is None or name is None or current_room is None:  # Check if user is in session
            if request.endpoint != "index":
                print("Redirect to index")
                return redirect(url_for("index"))  # Redirect to login if not logged in
            
        elif not current_room.get_room_status(): # Check if game is still in lobby
            if request.endpoint != "lobby":
                print("Redirect to lobby")
                return redirect(url_for("lobby"))
            
        elif current_room.get_room_status():
            if request.endpoint != "game":
                print("Redirect to game")
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
    if request.method == 'POST':
        username = request.form.get('username')
        action = request.form.get('action')

        if not username or username.strip() == "":
            context = { "err": True, "msg": "Enter a valid username" }
            return render_template('index.html', ctx=context)
        if action == "Create Room":
            room_code = room_manager.create_room(username)
            session["room"] = room_code
            session["name"] = username

            print("Create Room")
            return redirect(url_for('lobby'))
        elif action == "Join Room":
            code = request.form.get('join-code')
            joining_room = room_manager.get_room(code)

            if joining_room is not None and joining_room.get_room_status():
                context = { "err": True, "msg": "Game Started" }
                return render_template('index.html', ctx=context)
            
            if joining_room is not None:
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
    
    if request.method == "POST":
        action = request.form.get('action')

        if action == 'leave': 
            return redirect(url_for('logout'))
    
    lobby_room = room_manager.get_room(room)

    context = { "room": room, "is_admin": name == lobby_room.get_admin(), "admin": lobby_room.get_admin() }

    return render_template('lobby.html', ctx=context)

@app.route('/game', methods=['GET', 'POST'])
@login_required
def game():
    room = session.get("room")
    name = session.get("name")
    game_room = room_manager.get_room(room)

    if game_room is None:
        return redirect(url_for("index"))
    
    context={ "room": game_room.get_json_room(), "is_admin": name == game_room.get_admin() }
    return render_template('game.html', ctx=context)

class LobbyNamespace(Namespace):
    def on_connect(self):
        room = session.get("room")
        name = session.get("name")
        lobby_room = room_manager.get_room(room)

        if lobby_room is not None and name:
            print(f"User {name} joined room {room}")
            join_room(room)

            if lobby_room.get_admin() != name:
                lobby_room.add_player(name)

            socketio.emit("user_change", lobby_room.get_json_room(), namespace='/lobby', to=room)
        else:
            socketio.emit("player_left", {'msg': "gone"}, namespace='/lobby', to=request.sid)

    def on_disconnect(self, reason):
        room = session.get("room")
        name = session.get("name")
        lobby_room = room_manager.get_room(room)

        print(f"User {name} left room {room}")
        leave_room(room)

        if lobby_room is None or lobby_room.get_room_status():
            return
        
        if lobby_room.get_admin() == name:
            print(f"Delete room {room}")
            socketio.emit("player_left", {'msg': "gone"}, namespace='/lobby', to=room)
            room_manager.delete_room(room)
            return

        lobby_room.remove_player(name)

        socketio.emit("user_change", lobby_room.get_json_room(), namespace='/lobby', to=room)

    def on_start_game(self, data):
        room = session.get("room")
        lobby_room = room_manager.get_room(room)
        
        lobby_room.create_players_data()
        lobby_room.set_room_status(True)
        
        socketio.emit('game_start', {'message': 'Game is starting!'}, namespace='/lobby', to=room)

class GameNamespace(Namespace):
    def on_connect(self):
        room = session.get("room")
        name = session.get("name")
        sid = request.sid

        join_room(room)
        game_room = room_manager.get_room(room)

        if game_room is not None:
            print(f"User {name} SID updated: {sid}")
            game_room.set_sid_from_players(name, sid)
        else:
            disconnect()

    def on_disconnect(self, reason):
        room = session.get("room")
        leave_room(room)
        print("Game Disconnect")
    
    def on_get_stats(self):
        room = session.get("room")
        name = session.get("name")
        game_room = room_manager.get_room(room)

        if game_room.get_admin() == name:
            return
        
        data = game_room.get_player_data(name)
        player_sid = game_room.get_sid_from_players(name)

        data["currentRound"] = game_room.get_current_round()
        
        socketio.emit('send_stats', data, namespace='/game', to=player_sid)
        print(f"Sent Stats {data} to {name}")

    def on_submit_bid(self, data):
        room = session.get("room")
        name = session.get("name")
        if room not in rooms:
            disconnect()

        print(f"Before Parse: {data}")
        parsed_data = parse_qs(data.get('data', ''))
        print(f"Before Clean: {parsed_data}")
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
        
        print(parsed_data_clean)
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
            if (parsed_data_clean["quantity"] != 'd'):
                if (parsed_data_clean["quantity"] < 0 or parsed_data_clean["quantity"] > player.bids[0].units):
                    socketio.emit('bid_status', {'message': f'Enter a different quantity (ensure it is non-negative number below the number of units you have ({player.bids[0].units})'}, namespace='/game', to=player.sid)
                    return
            player.bids[0].price = float(parsed_data_clean["price"])
            if (parsed_data_clean["quantity"] == 'd'):
                player.bids[0].quantity = player.bids[0].units
            else:
                player.bids[0].quantity = float(parsed_data_clean["quantity"])
            player.hasBid = True
            
            socketio.emit('bid_status', {'message': 'Bid successful!'}, namespace='/game', to=player.sid)

            marketUnits = 0
            allBid = all(player.hasBid for player in rooms[room]["dataList"])
            if allBid:
                for player in rooms[room]["dataList"]:
                    for bid in player.bids:
                        marketUnits += bid.quantity

            data = {
                "allBid": allBid,
                "name": player.name,
                "marketUnits": marketUnits
            }

            socketio.emit('all_bids_status', data, namespace='/game', to=room)
 
        print(f"{name} submit data: {parsed_data_clean}")

    def on_run_round(self, data):
        room = session.get("room")
        name = session.get("name")

        if name != rooms[room]["admin"]["username"]:
            return

        # Check if everyone has voted
        if all(player.hasBid for player in rooms[room]["dataList"]):
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
            demand = parsed_data_clean["slider"]
            print(f"This is the demand: {demand}")

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
            sorted_player_profits = sorted(player_profits, key=lambda x: x["total"], reverse=True)
            data =  {
                        "graphData": graphData,
                        "playerProfits": sorted_player_profits,
                        "roundNumber": rooms[room]["game"]["currentRound"] + 1
                    }
            
            socketio.emit('round_over', data, namespace='/game', to=room)
            for player in rooms[room]["dataList"]:
                player.hasBid = False

            rooms[room]["game"]["currentRound"] += 1
        else:
            socketio.emit('bid_status', {'message': f'Not everyone has voted!'}, namespace='/game', to=rooms[room]["admin"]["sid"])

socketio.on_namespace(LobbyNamespace('/lobby'))
socketio.on_namespace(GameNamespace('/game'))

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
