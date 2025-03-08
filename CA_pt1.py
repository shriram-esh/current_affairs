import numpy as np
from scipy.optimize import minimize
import random
from scipy.optimize import linprog

#defines each bidder
class Data:
    
    def __init__(self, name, bid_size, profit): #GIVE PLAYERS AN INITIAL CAPITAL
        self.name = name #identify the player
        self.bids = []*bid_size
        self.profit = profit
        self.hist = []

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
        self.bids = bids
        self.profit = profit
        self.round_num = round_num

    def __str__(self):
         return f"ended round {self.round_num+1} with ${self.profit}"
        # return f"Cleared {self.quantity} units at ${self.price}, ending the round with ${self.profit}"


#Data taken roughly from https://en.wikipedia.org/wiki/Cost_of_electricity_by_source and https://www.eia.gov/energyexplained/electricity/electricity-in-the-us-generation-capacity-and-sales.php
# each tuple of the form (energy type, cost of generation, max generation)

#ASSETS WE DEFINED FEB 19
total = 3000
# assets = [("Wind Power", 0, 0.2*(total)),   #0 
#           ("Hydropower", 0, 0.1*(total)),   #1
#           ("Coal", 200, 0.2*(total)),       #2
#           ("Nuclear", 10, 0.1*(total)),     #3
#           ("Bio-mass", 30, 0.05*(total)),   #4
#           ("Gas", 100, 0.30*(total)),       #5
#           ("Solar", 0, 0.05*(total))]       #6
        #GIVE EACH POWER PLANT A CAPACITY

#ASSETS FROM QUESTION MAKE TO FIZED QUATNTITY INDEASD OF FIXED TOTAL CAN BID UP TO UNITS THEY HAVE (15 or SO)
assets = [("Wind Power", 75, 0.2*(total)),  #0
          ("Nuclear", 15, 0.1*(total)),     #1
          ("Solar", 0, 0.05*(total)),       #2
          ("CHP", 42, 0.05*(total)),        #3
          ("Hydropower", 10, 0.1*(total))]  #4


##########################
#DEFINE THE NUMBER OF PLAYERS AND INITIALIZE THEM
##########################
def define_players(starting_units):
    cap_initial_units = 10
    num_players = int(input("Enter the number of players: "))

    #prompt for data input into array
    data_list = []
    ids = [] #the players names serve as their unique ID, this array will hold all the IDs

    #define all the players
    for i in range(num_players):
        # temp = Data
        name = (input("Please enter a unique username: "))
        while(name in ids or name == ""):
            name= input("Please enter different username that hasn't been taken: ")

        ids.append(name)
        profit = 0
        data_list.append(Data(name, starting_units, profit))

        # print(f"you start with ${profit}")
        # for j in range(starting_units):
        for j in range(starting_units):
            #rand_elem = random.randint(0, len(assets)-1)
            data_list[i].bids.append(bid(0,0,0,0))

            asset_num = -1
            while asset_num<0 or asset_num>(len(assets)-1):
                 asset_num = int(input("Enter the asset number (from the array): "))

            data_list[i].bids[j].asset = asset_num
            data_list[i].bids[j].units = int(input("Enter the starting number of units: "))
            # print(f"and {data_list[i].bids[j].units} units of {assets[data_list[i].bids[j].asset][0]}")

        # for b in data_list[i].bids:    
        #     print(f"and {b.units} units of {assets[b.asset][0]} who's cost of generation is {assets[b.asset][1]} and who's max generation is {assets[b.asset][2]}")
        # print("")

        print(f"you start with ${profit}")
        for k in range(starting_units):
            print(f"and {data_list[i].bids[k].units} units of {assets[data_list[i].bids[k].asset][0]} who's cost of generation is {assets[data_list[i].bids[k].asset][1]} and who's max generation is {assets[data_list[i].bids[k].asset][2]}")
        print("")

    return data_list, ids


######################
#ASK EACH PLAYER FOR A LEGAL BID
######################
def get_bids(players, market_cap): #WHAT IS THE MAX QUANTITY YOU CAN BID? THE NUMBER OF UNITS YOU HAVE OR SMTH TO DO WITH MAX GENERATION?
    for temp in (players):
        Len = len(temp.bids)
        for i in range(Len):
            price = ((input(f"{temp.name}, enter the price of your bid for {assets[temp.bids[i].asset][0]} or 'd' for the default bid: ")))
            if price == "d":
                 temp.bids[i].price = assets[temp.bids[i].asset][1]
                 temp.bids[i].quantity = temp.bids[i].units
                 print(f"${temp.bids[i].price} bid for {temp.bids[i].quantity} units")
                 continue
            
            while((not price.isdigit()) or (price.isdigit() and (float(price) < 0 or float(price) > market_cap))):
                    price = ((input("Please enter a differnt price (ensure it is non-negative number below the market cap): ")))

            temp.bids[i].price = (float(price))

            quantity = ((input(f"{temp.name} enter the quantity of your bid: ")))                 
            while((not quantity.isdigit()) or (quantity.isdigit() and (float(quantity) < 0 or float(quantity) > assets[temp.bids[i].asset][2]))):
                    quantity=((input("Please enter a differnt quantity (ensure it is non-negative number below the generator's max generation): ")))

            temp.bids[i].quantity = (float(quantity))
        print(" ")


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
        





def playRound(starting_units, market_cap, players, ids, round_num):
    Demand = int(input("Enter the demand for this round: "))
    get_bids(players, market_cap)

    c = [] #prices
    u = [] #quantities of each good
    b_eq = [Demand, 0]

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
    if(sum(u)>=Demand):
        # res = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='simplex', options={"tol": 1e-6})
        res = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=bounds)
        print(f"The marginal returned from LinProg: {res.eqlin["marginals"]}")
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
how_many_rounds = int(input("Enter the number of rounds to play: "))
starting_units = int(input("Enter the number of units each player starts with: "))
market_cap = int(input("Enter the Market Cap: "))
print(" ")

players, ids = define_players(starting_units)
print(ids)

count=0
while (count < how_many_rounds) and (len(players)>1):
    print(f"Length of players: {len(players)}")
    players, ids = playRound(starting_units, market_cap, players, ids, count)
    count+=1

    print("history up to this point for remaining players: ")
    for p in players:
        for h in p.hist:
            print(f"{p.name} {h}")
        #     for b in h.bids:
        #         print(f"and bid {b.quantity} units of {assets[b.asset][0]} at ${b.price}")
        #     print("")
        # print("")
