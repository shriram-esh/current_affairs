import random
import json


assets = [
    ("Coal", 30, 2000),                         ("Natural Gas (Combined Cycle)", 95, 1000),
    ("Natural Gas (Open Cycle)", 100, 500),     ("Nuclear", 90, 600),
    ("Wind (onshore)", 2.5, 10),                ("Wind (Offshore)", 2.5, 10),
    ("Solar Photovoltaic", 2.5, 500),           ("Concentrated Solar Power", 2.5, 100),
    ("Large-Scale Hydropower", 15, 300),        ("Geothermal", 70, 70),
    ("Biomass (Wood)", 25, 70),                 ("Biomass (Agricultural Waste)", 45, 30),
    ("Biogas (Landfills)", 60, 10),             ("Tidal Power", 2.5, 3),
    ("Wave Power", 2.5, 4),                     ("Hydrogen Fuel Cells", 100, 3),
    ("Waste-to-Energy (Incineration)", 60, 10), ("Waste-to-Energy (Landfill Gas)", 50, 1),
    ("Hydrogen Gas Turbine", 150, 200),         ("Compressed Air Energy", 50, 10),
    ("Pumped Storage Hydroelectric", 20, 100),  ("Shale Oil Power Generation", 150, 10),
    ("Coal-to-Liquid", 35, 100),                ("Concentrated Solar Thermal", 2.5, 50),
    ("Organic Photovoltaic", 2.5, 1),           ("Microgrids (Renewable)", 10, 5),
    ("Small Modular Reactors", 0, 100),         ("Ocean Thermal Energy Conversion", 2.5, 20),
    ("Algae Biofuel", 80, 20),                  ("Magnetohydrodynamic", 10, 100) 
] 

def get_random_rgba():
    return f"rgba({random.randint(0,255)},{random.randint(0,255)},{random.randint(0,255)},1)"

class Bid:
    def __init__(self, asset, units, price, quantity):
        self.asset = asset
        self.units = units
        self.price = price
        self.quantity = quantity
    
    # "get_units" returns units
    # inputs: none
    # output: units (int)
    def get_units(self):
        return self.units
    
    # "get_json_bid" returns json object for Bid class
    # input: none
    # output: json object 
    def get_json_bid(self):
        x = {
            "asset": self.asset, 
            "units": self.units,
            "price": self.price,
            "quantity": self.quantity 
        }
        return json.dumps(x)

class Data:
    def __init__(self, username, bid_size, profit):
        self.username = username 
        self.bids = [] * bid_size 
        self.profit = profit
        self.color = get_random_rgba()
        self.hasBid = False

    # Start Functions

    # "get_player_bids" gets the name of the player
    # input: username (string)
    # output: bids [json_object, json_object]
    # NOTE call get_json_bid for each bid before returning it
    #QUESTION Im not sure what the username input is for cause like i dont think data has acess to the list of players
    def get_player_bids(self, username):
        json_bids = [b.get_json_data() for b in self.bids]
        return json_bids

    # "has_player_bid" gets if the player had bid
    # input: none
    # output: hasBid (boolean)
    def has_player_bid(self):
        return self.hasBid

    # "get_all_player_units" should call get_units from Bid class
    # input: none
    # output: toal_bid_units (int)
    def get_all_player_units(self):
        count = 0
        for b in self.bids:
            coutn += b.get_units()
        return count

    # "set_bid_status" should set biStatus to input
    # input: status (boolean)
    # output: none
    def set_bid_status(self, input):
        self.hasbid = input

    # "get_json_data" returns json object for Data class
    # input: none
    # output: json object 
    def get_json_data(self):

        x = { 
            "username": self.username, 
            "bids": self.get_player_bids(self.username),
            "profit": self.profit,
            "color": self.color,
            "hasBid": self.hasBid 
            }
        return json.dumps(x)


class Player:
    def __init__(self, username, sid=""):
        self.username = username
        self.sid = sid
    
    # Start Functions

    # "get_player_name" gets the name of the player
    # input: none
    # output: username (string)
    def get_player_name(self):
        return self.username

    # "get_player_sid" gets the sid of the player
    # input: none
    # output: sid (string)
    def get_player_sid(self):
        return self.sid

    # "set_player_sid" sets the sid of the player
    # input: sid (string)
    # output: none
    def set_player_sid(self, input_sid):
        self.sid = input_sid

    # "get_json_player" returns json object for Player class
    # input: none
    # output: json object { "username": username, "sid": sid }
    def get_json_player(self):
        x = {
            "username": self.username, 
            "sid": self.sid
        }

        # convert into JSON:
        return json.dumps(x)

    

class Room:
    def __init__(self, admin_username):
        self.admin = Player(admin_username)
        self.players = []  # List of Player objects
        self.playersData = []  # List of Data objects
        self.game = {"started": False, "currentRound": 1}

    # Start Functions

    def add_player(self, username, sid=""):
        self.players.append(Player(username, sid))

    def add_data(self, name, bid_size, profit):
        self.playersData.append(Data(name, bid_size, profit))

    # "get_room_status" gets the game status "started"
    # input: none
    # output: game_status (boolean)
    def get_room_status(self):
        return self.game["started"]

    # "set_room_status" sets the game status "started"
    # input: game_status (boolean)
    # output: none
    def set_room_status(self, input_game_status):
        self.game["started"] = input_game_status
        #QUESTION should this take an input, or just change the member variable

    # "remove_player" removes player from room
    # input: username (string)
    # output: none
    def remove_player(self, name):
        self.players.remove(name)

    # "create_playersData" randomizes the quantity and portfolio for everyone
    # input: none (assets are above and players are in this class)
    # output: none
    # NOTE I'm not sure about this but just implement the define_players code in this function to work
    def create_playersData(self):
        asset_indexes = list(range(len(assets)))
        for d in self.playersData:
            for b in d.bids:
                assets_indexes = asset_indexes if assets_indexes == [] else list(range(len(assets)))
                rand_asset = random.choice(asset_indexes)
                asset_indexes.remove(rand_asset)
                b.asset = assets[rand_asset[1]] #QUESTION do you just want the string part?
                b.units = random.randint(400, 800)
                b.price = assets[rand_asset[2]]
                b. quantity = random.randint(400, 800) #QUESTION i lowk forgot the difference between asset and units, so I initialized to same range

    # TODO "get_sid_from_players" should call get_player_sid in player class
    # input: username (string)
    # output: sid (string)
    def get_sid_from_players(self, input_username):
        p = self.get_player(input_username)
        return p.get_player_sid()

    # TODO "set_sid_from_players" should call set_player_sid in player class
    # input: username (string), sid (string)
    # output: none
    def set_sid_from_players(self, input_username, input_sid):
        p = self.get_player(input_username)
        p.set_player_sid(input_sid)

    # TODO "get_player_data" should call set_player_sid in player class
    # input: username (string)
    # output: data ([{"asset": ..., "units": ..., "generation": ..., "currentRound": ...}, ...])
    def get_player_data(self, input_username):
        data = []
        p = self.get_data(input_username)
        for b in p.bids:
            data.append(p.get_json_data())#QUESTION did u want this output as a json? and can the currentRound be a seperate function? (i made it below) cause it would be the same for each bid right?
        return data
    
    # TODO "get_player_bid_status" should call has_player_bid in Data class
    # input: username (string)
    # output: hasBid (boolean)
    def get_player_bid_status(self, input_username):
        d = self.get_data(input_username)
        return d.has_player_bid()


    # TODO "has_all_players_bid" return whether all players have bid (call has_player_bid)
    # input: none
    # output: yes (boolean)
    def has_all_players_bid(self):
        for d in self.playersData:
            if(not d.has_player_bid()):
                return False
        return True
    
    # TODO "set_all_players_bid_status" call set_bid_status in Data class
    # input: status (boolean)
    # output: none
    def set_all_players_bid_status(self, input_status):
        for p in self.playersData:
            p.set_bid_status(input_status)

    # TODO "get_total_units" call get_all_player_units
    # input: none
    # output: yes (boolean)
    def get_total_units(self):
        count = 0
        for d in self.playersData:
            for b in d.bids:
                count += len(b)
        return count #QUESTION do you want a bool or like the number

    # TODO "get_current_round" return the current round
    # input: none
    # output: round (int)
    def get_current_round(self):
        return self.game["currentRound"]

    # TODO "increment_round" add +1 to round
    # input: none
    # output: none
    def increment_round(self):
        self.game["currentRound"] = self.game["currentRound"]+1

    # TODO "get_json_room" returns a json object for Room class
    # NOTE you will need to call the json object functions for the "admin", "players", and "playersData"
    # input: none
    # output: json_object 
    def get_json_room(self):
        x = {
            "admin": self.admin.get_json_player(),
            "players": [p.get_json_player() for p in self.players], #(call get_json_player on each element of the array),
            "playersData": [d.get_json_data() for d in self.playersData], #(call get_json_data on each element of the array),
            "game": self.game
            }
        return json.dumps(x)

    #returns the player given a username (used as a private function)
    def get_player(self, input_username):
        return next((obj for obj in self.players if obj.username == input_username), None)
    
    def get_data(self, input_username):
        return next((obj for obj in self.playersData if obj.username == input_username), None)

class RoomManager:
    def __init__(self):
        self.rooms = {} # dictionary of Room classes

    # Start Functions
    # Here is an example of a function
    def create_room(self, admin_username, room_code):
        self.rooms[room_code] = Room(admin_username)

    # TODO "delete_room" deletes the room from rooms
    # input: room_code (string)
    # output: none
    def delete_room(self, input_room_code):
        del self.rooms[input_room_code]
        
    # TODO "get_rooms" returns all the room codes
    # input: none
    # output: rooms dictionary ({})
    def get_rooms(self):
        return self.rooms

    # TODO "get_game_status" this should call "get_room_status" (Look in Rooms class)
    # input: room_code (string)
    # output: game_status (boolean)
    def get_game_status(self, input_room_code):
        return (self.rooms[input_room_code]).get_room_status()

    # TODO "set_game_status" this should call "set_room_status" (Look in Rooms class)
    # input: room_code (string), game_status (boolean)
    # output: none
    def set_game_status(self, input_room_code, input_game_status):
        return (self.rooms[input_room_code]).set_room_status(input_game_status)

    # TODO "get_sid_from_players_room" should call get_sid_from_players in Room class
    # input: username (string)
    # output: sid (string)
    def get_sid_from_players_room(self, input_username, input_room_code):#QUESTION wouldnt this also need the room code?
        return self.rooms[input_room_code].get_sid_from_players(input_username)

    # TODO "set_sid_from_players_room" should call set_sid_from_players in Room class
    # input: username (string), sid (string)
    # output: none
    def set_sid_from_players_room(self, input_room_code, input_username, input_sid):#QUESTION doenst this need room code too?
        self.rooms[input_room_code].set_sid_from_players(input_username, input_sid)

    # TODO "get_player_stats" should call get_player_data
    # input: username (string)
    # output: data ([{"asset": ..., "units": ..., "generation": ..., "currentRound": ...}, ...])
    def get_player_stats(self, input_room_code, input_username):#QUESTION room code here too?
        return self.rooms[input_room_code].get_player_data(input_username)

    # TODO "get_players_room_bid_status" should call get_player_bid_status in Room class
    # input: username (string)
    # output: yes (boolean)
    def get_players_room_bid_status(self, input_room_code, input_username):
        return self.rooms[input_room_code].get_player_bid_status(input_username)

    # TODO "get_rooms_total_bid_units" call get_total_units
    # input: code (string)
    # output: units (int)
    def get_rooms_total_bid_units(self, input_room_code):
        return self.rooms[input_room_code].get_total_units()

    # TODO "get_room_current_round" call get_current_round in Room class
    # input: code (string)
    # output: round (int)
    def get_room_current_round(self, input_room_code):
        return self.rooms[input_room_code].get_current_round()

    # TODO "increment_room_round" call increment_round in Room class
    # input: code (string)
    # output: none
    def increment_room_round(self, input_room_code):
        return self.rooms[input_room_code].increment_round()


    # TODO "set_all_players_in_room_bid_status" call set_all_players_bid_status in Room class
    # input: code (string), status (boolean)
    # output: none
    def set_all_players_in_room_bid_status(self, input_room_code, input_status):
        return self.rooms[input_room_code].set_all_players_bid_status(input_status)
