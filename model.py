import random

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
    
    # TODO "get_units" returns units
    # inputs: none
    # output: units (int)
    
    # TODO "get_json_bid" returns json object for Bid class
    # input: none
    # output: json object 
    # { 
    #   "asset": asset, 
    #   "units": units,
    #   "price": price,
    #   "quantity": quantity 
    # }

class Data:
    def __init__(self, username, bid_size, profit):
        self.username = username 
        self.bids = [] * bid_size 
        self.profit = profit
        self.color = get_random_rgba()
        self.hasBid = False

    # Start Functions

    # TODO "get_player_bids" gets the name of the player
    # input: username (string)
    # output: bids [json_object, json_object]
    # NOTE call get_json_bid for each bid before returning it

    # TODO "has_player_bid" gets if the player had bid
    # input: none
    # output: hasBid (boolean)

    # TODO "get_all_player_units" should call get_units from Bid class
    # input: none
    # output: toal_bid_units (int)

    # TODO "set_bid_status" should set biStatus to input
    # input: status (boolean)
    # output: none

    # TODO "get_json_data" returns json object for Data class
    # input: none
    # output: json object 
    # { 
    #   "username": username, 
    #   "bids": [] (call get_json_bid on each element of the array),
    #   "profit": profit,
    #   "color": color,
    #   "hasBid": hasBid 
    # }

class Player:
    def __init__(self, username, sid=""):
        self.username = username
        self.sid = sid
    
    # Start Functions

    # TODO "get_player_name" gets the name of the player
    # input: none
    # output: username (string)

    # TODO "get_player_sid" gets the sid of the player
    # input: none
    # output: sid (string)

    # TODO "set_player_sid" sets the sid of the player
    # input: sid (string)
    # output: none

    # TODO "get_json_player" returns json object for Player class
    # input: none
    # output: json object { "username": username, "sid": sid }
    

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
        self.datalist.append(Data(name, bid_size, profit))

    # TODO "get_room_status" gets the game status "started"
    # input: none
    # output: game_status (boolean)

    # TODO "set_room_status" sets the game status "started"
    # input: game_status (boolean)
    # output: none

    # TODO "remove_player" removes player from room
    # input: username (string)
    # output: none

    # TODO "create_playersData" randomizes the quantity and portfolio for everyone
    # input: none (assets are above and players are in this class)
    # output: none
    # NOTE I'm not sure about this but just implement the define_players code in this function to work

    # TODO "get_sid_from_players" should call get_player_sid in player class
    # input: username (string)
    # output: sid (string)

    # TODO "set_sid_from_players" should call set_player_sid in player class
    # input: username (string), sid (string)
    # output: none

    # TODO "get_player_data" should call set_player_sid in player class
    # input: username (string)
    # output: data ([{"asset": ..., "units": ..., "generation": ..., "currentRound": ...}, ...])

    # TODO "get_player_bid_status" should call has_player_bid in Data class
    # input: username (string)
    # output: hasBid (boolean)

    # TODO "has_all_players_bid" return whether all players have bid (call has_player_bid)
    # input: none
    # output: yes (boolean)

    # TODO "set_all_players_bid_status" call set_bid_status in Data class
    # input: status (boolean)
    # output: none

    # TODO "get_total_units" call get_all_player_units
    # input: none
    # output: yes (boolean)

    # TODO "get_current_round" return the current round
    # input: none
    # output: round (int)

    # TODO "increment_round" add +1 to round
    # input: none
    # output: none

    # TODO "get_json_room" returns a json object for Room class
    # NOTE you will need to call the json object functions for the "admin", "players", and "playersData"
    # input: none
    # output: json_object 
    # {
    #   "admin": get_json_player,
    #   "players": [] (call get_json_player on each element of the array),
    #   "playersData": [] (call get_json_data on each element of the array),
    #   "game": game
    # }

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

    # TODO "get_rooms" returns all the room codes
    # input: none
    # output: rooms dictionary ({})

    # TODO "get_game_status" this should call "get_room_status" (Look in Rooms class)
    # input: room_code (string)
    # output: game_status (boolean)

    # TODO "set_game_status" this should call "set_room_status" (Look in Rooms class)
    # input: room_code (string), game_status (boolean)
    # output: none

    # TODO "get_sid_from_players_room" should call get_sid_from_players in Room class
    # input: username (string)
    # output: sid (string)

    # TODO "set_sid_from_players_room" should call set_sid_from_players in Room class
    # input: username (string), sid (string)
    # output: none

    # TODO "get_player_stats" should call get_player_data
    # input: username (string)
    # output: data ([{"asset": ..., "units": ..., "generation": ..., "currentRound": ...}, ...])

    # TODO "get_players_room_bid_status" should call get_player_bid_status in Room class
    # input: username (string)
    # output: yes (boolean)

    # TODO "get_rooms_total_bid_units" call get_total_units
    # input: code (string)
    # output: units (int)

    # TODO "get_room_current_round" call get_current_round in Room class
    # input: code (string)
    # output: round (int)

    # TODO "increment_room_round" call increment_round in Room class
    # input: code (string)
    # output: none

    # TODO "set_all_players_in_room_bid_status" call set_all_players_bid_status in Room class
    # input: code (string), status (boolean)
    # output: none