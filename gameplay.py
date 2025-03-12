import numpy as np
from scipy.optimize import minimize
import random
from scipy.optimize import linprog

def get_random_rgba():
    r = random.randint(0, 255)  # Random red (0-255)
    g = random.randint(0, 255)  # Random green (0-255)
    b = random.randint(0, 255)  # Random blue (0-255)
    return (r, g, b)

#defines each bidder
class Data:
    
    def __init__(self, name, bid_size, profit): #GIVE PLAYERS AN INITIAL CAPITAL
        self.name = name #identify the player
        self.bids = []*bid_size
        self.profit = profit
        self.hist = []
        self.color = get_random_rgba()
        self.hasBid = False
        self.sid = ""

class bid:
    def __init__(self, asset, units, price, quantity):
        self.asset = asset #index of the asset in the asset array
        self.units = units
        self.price = price
        self.quantity = quantity


class History:
    
    def __init__(self, profit, round_num, bids):
        # self.price = price
        # self.quantity_cleared = quantity_cleared
        self.bids = bids #what was bid NOT what was cleared
        self.profit = profit
        self.round_num = round_num

    def __str__(self):
        str_to_print = f"\n"
        for b in self.bids:
            str_to_print += f"and bid {b.quantity} units of {assets[b.asset][0]} at ${b.price}\n"
        return f"ended round {self.round_num+1} with ${self.profit} {str_to_print}"
        # return f"Cleared {self.quantity} units at ${self.price}, ending the round with ${self.profit}"

#Data taken roughly from https://en.wikipedia.org/wiki/Cost_of_electricity_by_source and https://www.eia.gov/energyexplained/electricity/electricity-in-the-us-generation-capacity-and-sales.php
# each tuple of the form (energy type, cost of generation, max generation)

#ASSETS WE DEFINED FEB 19
assets = [
    ("Coal", 140, 2000),                        ("Natural Gas (Combined Cycle)", 120, 1000),
    ("Natural Gas (Open Cycle)", 150, 500),     ("Nuclear", 90, 600),
    ("Wind (onshore)", 20, 10),                 ("Wind (Offshore)", 60, 10),
    ("Soloar Photovoltaic", 30, 500),           ("Concentrated Solar Power", 80, 100),
    ("Large-Scale Hydropower", 60, 300),        ("Geothermal", 70, 70),
    ("Biomass (Wood)", 50, 70),                 ("Biomass (Agricultural Waste)",100, 30),
    ("Biogas (Landfills)", 80, 10),             ("Tidal Power", 150, 3),
    ("Wave Power", 100, 4),                     ("Hydrogen Fuel Cells", 100, 3),
    ("Waste-to-Energy (Incineration)", 60, 10), ("Waste-to-Energy (Landfill Gas)", 50, 1),
    ("Hydrogen Gas Turbine", 70, 200),          ("Compressed Air Energy", 80, 10),
    ("Pumped Storage Hydroelectric", 40, 100),  ("Shale Oil Power Generation", 100, 10),
    ("Coal-to-Liquid", 200, 100),               ("Concentrated Solar Thermal", 80, 50),
    ("Organic Photovoltaic", 100, 1),           ("Microgrids (Renewable)", 75, 5),
    ("Small Modular Reactors", 90, 100),        ("Ocean Thermal Energy Conversion", 200, 20),
    ("Algal Biofuel", 150, 20),                ("Magnetohydrodynamic", 150, 100) 
] 

# GLOBAL VARIABLES
how_many_rounds = 15
market_cap = int(9000)
usable_assets = list(range(len(assets)))

        # GIVE EACH POWER PLANT A CAPACITY

# #ASSETS FROM QUESTION
# assets = [("Wind Power", 75, 0.2*(total)),  #0
#           ("Nuclear", 15, 0.1*(total)),     #1
#           ("Solar", 0, 0.05*(total)),       #2
#           ("CHP", 42, 0.05*(total)),        #3
#           ("Hydropower", 10, 0.1*(total))]  #4


##########################
#DEFINE THE NUMBER OF PLAYERS AND INITIALIZE THEM
##########################
def define_players(usable_assets, players):
    # Players will be data with username
    data_list = [] # this will be in the rooms[room] data structure

    #define all the players
    for index, player in enumerate(players):
        data_list.append(Data(player["username"], 1, 0))
        
        add_asset(usable_assets, data_list[index])

    return data_list

#adds one asset to one player
def add_asset(usable_assets, player):
    #rand_elem = random.randint(0, len(assets)-1)
    if len(usable_assets) == 0:
        usable_assets = list(range(len(assets)))

    asset_num = int(random.randint(0,len(usable_assets)-1))#retruns the index of the usable_assets list. at that index is the index of the asset

    player.bids.append(bid(usable_assets[asset_num],int(random.randint(1,10)),0,0))
    usable_assets.pop(asset_num)


######################
#ASK EACH PLAYER FOR A LEGAL BID
######################
# def get_bids(players, market_cap): #WHAT IS THE MAX QUANTITY YOU CAN BID? THE NUMBER OF UNITS YOU HAVE OR SMTH TO DO WITH MAX GENERATION?
#     for temp in (players):
#         Len = len(temp.bids)
#         for i in range(Len):
#             price = ((input(f"{temp.name}, enter the price of your bid for {assets[temp.bids[i].asset][0]} or 'd' for the default bid: ")))
#             if price == "d":
#                  temp.bids[i].price = assets[temp.bids[i].asset][1]
#                  temp.bids[i].quantity = temp.bids[i].units
#                  print(f"${temp.bids[i].price} bid for {temp.bids[i].quantity} units")
#                  continue
            
#             while((not price.isdigit()) or (price.isdigit() and (float(price) < 0 or float(price) > market_cap))):
#                     price = ((input("Please enter a differnt price (ensure it is non-negative number below the market cap): ")))

#             temp.bids[i].price = (float(price))

#             quantity = ((input(f"{temp.name} enter the quantity of your bid: ")))                 
#             while((not quantity.isdigit()) or (quantity.isdigit() and (float(quantity) < 0 or float(quantity) > temp.bids[i].units))): #assets[temp.bids[i].asset][2]) = max generation
#                     quantity=((input("Please enter a differnt quantity (ensure it is non-negative number below the number of units you have): ")))

#             temp.bids[i].quantity = (float(quantity))
#         print(" ")


####################
#PRINT THE DETAILS OF THE LAST ROUND:
#DEMAND, MARKET_PRICE, PROFIT OF EACH PLAYER
####################
def print_results(Demand, market_price, data_list):
    #print the Demand and market price 
    print(f"For a demand of: {Demand}")
    print(f"The Market price was: {market_price}")
    print(f"The Demand Charges: {market_price * Demand}\n\n")


    #print the profits for each player
    for dat in data_list:
        print(f"profits for {dat.name}: {dat.profit}")


###############
#UPDATES THE HISTORY ARR OF EACH PLAYER
###############
def update_history(data_list, round_num):
    for temp in (data_list):
        (temp.hist).append(History(temp.profit, round_num, temp.bids))
        
def playRound(players, round_num, demand):
    # get_bids(players, market_cap)

    c = [] #prices
    u = [] #quantities of each good
    b_eq = [demand, 0]

    #unzip the peoples bids into one vector
    for person in players:
        for b in person.bids:
            c.append(b.price)
            u.append(b.quantity)

    #l = [0]*len(c)
    A_eq = [[1]*len(c), [0]*len(c)]
    bounds = []
    for upper_bound in u:
        bounds.append((0, upper_bound))

    #define the quantities cleared and market price USING MAGIC
    if(sum(u)>=demand):
        # res = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='simplex', options={"tol": 1e-6})
        res = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=bounds)
        print(f"The marginal returned from LinProg: {res.eqlin['marginals']}")
        market_price = res.eqlin["marginals"][0]
        print(f"The vector x returned from LinProg{res.x}\n\n")
        x = res.x
    
    else: #if the demand was not met, then the cleared quantities is the bid quantities, and the market price is the highest price
        print("Supply did not meet the Demand so all quantitties are cleared")
        print(f"Quantities bid: {u}\n")
        market_price = max(c)
        x = u

    #calculate people's profits
    count = 0 #parsing the x vector
    for person in players:
        for b in person.bids:
            if count < len(x):
                person.profit += (market_price - assets[b.asset][1])*x[count] # (market price - cost of generation) * quanitty cleared
            count += 1 
        print(f"{person.name} ended round {round_num} with profit {person.profit}")
    print("\n\n")
            # make it output what just happened in one round - without too much random

    # for x in players:
    #     print(f"profits for {x.name}: {x.profit}")

    players = [x for x in players if x.profit > 0]
    print(f"if you are bankrupt, you are being kicked out :(")
    #print(f"Lenth of PLayers after removed: {len(players)}")

    ids = [x.name for x in players]
    print(f"players left {ids}")

    print_results(Demand, market_price, players)
    update_history(players, round_num)

    return players, ids



################
##MAIN FUNCTION
################

# players = define_players(usable_assets)

# count=0
# while (count < how_many_rounds) and (len(players)>1):
#     print(f"Length of players: {len(players)}")
#     players, ids = playRound(market_cap, players, ids, count)
#     count+=1

#     if count%2 == 0:
#          for p in players:
#               add_asset(usable_assets, p)

#     print("history up to this point for remaining players: ")
#     for p in players:
#         for h in p.hist:
#             print(f"{p.name} {h} \n")