import random

#defines each bidder
class Data:

    def __init__(self, name, price, quantity, profit, asset, units, hist): #GIVE PLAYERS AN INITIAL CAPITAL
        self.name = name #identify the player
        self.price = price #bid quantity - should it be bounded somehow by thier physical assets? I have to seperate bid and price and create rounds
        self.quantity = quantity
        self.profit = float(profit)
        self.units = units#the index coresponds to the index in asset
        self.asset = asset#an int is saved that is the index of the asset in the assets arr
        self.hist = hist

# class History:
    
#     def __init__(self, price, quantity, profit):
#         self.price = price
#         self.quantity = quantity
#         self.profit = profit

#     def __str__(self):
#         return f"Bid {self.quantity} units at ${self.price}, giving a profit of ${self.profit}"


#Data taken roughly from https://en.wikipedia.org/wiki/Cost_of_electricity_by_source and https://www.eia.gov/energyexplained/electricity/electricity-in-the-us-generation-capacity-and-sales.php
# each tuple of the form (energy type, cost of generation, max generation)
assets = [("Wind Power", 1718, 4340), ("Hydropower", 3083, 2550), ("Coal", 4074, 6750), ("Nuclear", 7123, 7780), ("Bio-mass", 4524, 4700), #GIVE EACH POWER PLANT A CAPACITY
            ("Geo-theraml",3076, 1600), ("Solar", 1524, 2440)]

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
        profit = random.randint(int(market_cap/4), market_cap)
        data_list.append(Data(name,[] ,[] ,profit ,[] , [], []))

        for j in range(starting_units):
            rand_elem = random.randint(0, len(assets)-1)
            data_list[i].asset.append(rand_elem)
            data_list[i].units.append(random.randint(1, cap_initial_units)) 

        print(f"you start with ${profit}")
        for k in range(starting_units):
            print(f"and {data_list[i].units[k]} units of {assets[data_list[i].asset[k]][0]} who's cost of generation is {assets[data_list[i].asset[k]][1]} and who's max generation is {assets[data_list[i].asset[k]][2]}")
        print("")

    return data_list, ids


######################
#ASK EACH PLAYER FOR A LEGAL BID
######################
def get_bids(players, market_cap):
    for temp in (players):
        Len = len(temp.asset)
        for i in range(Len):
            price = ((input(f"{temp.name}, enter the price of your bid for {assets[temp.asset[i]][0]}: ")))
            while((not price.isdigit()) or (price.isdigit() and (float(price) < 0 or float(price) > market_cap))):
                    price = ((input("Please enter a differnt price (ensure it is non-negative number below the market cap): ")))

            temp.price.append(float(price))

            quantity = ((input(f"{temp.name} enter the quantity of your bid: ")))
            while((not quantity.isdigit()) or (quantity.isdigit() and (float(quantity) < 0 or float(quantity) > assets[temp.asset[i]][2]))):
                    quantity=((input("Please enter a differnt quantity (ensure it is non-negative number below the generator's max generation): ")))
            temp.quantity.append(float(quantity))
        print(" ")


#####################
#DEFINE THE PROFOTS FOR EACH PLAYER
#DEFINE IF A PLAYER HAS BEEN FULLY CLEARED
#####################
def players_profits(Demand, sorted_data_list, data_list):
    #sort the data so we can go over it in order of the graph
    Size = len(sorted_data_list)
    Quantity_Sum=0
    Count = 0

    ###################
    #CLEAR PLAYERS (will over clear a few that should be partially cleared)
    ###################

    #while the total quantity so far is less than the demand, clear the next bidder and their quantity
    while(Quantity_Sum<Demand and Count<Size):
        Quantity_Sum += sorted_data_list[Count][1]
        sorted_data_list[Count][3] = True
        Count+=1

    Count -= 1 #the bidder at this index of the sorted array defines the market_price from their price
    market_price = sorted_data_list[Count][2]
    # print(f"with demand {Demand} and quantity sum: {Quantity_Sum}")
    quantity_partially_cleared = Demand - Quantity_Sum #the overcounting if we add together the quantities of partially cleared
    if(quantity_partially_cleared>0):
        print("The demand was not met, so every quantity is cleared")
        for dat in sorted_data_list:
            for x in data_list:
                if(x.name == dat[0]):
                    x.profit += float(market_price - dat[2])*dat[1]
        return market_price

    ###################
    #GATHER THE PARTIALLY CLEARED AND CORRECT FOR THE OVERCLEARING
    ###################

    partially_cleared = []

        #check the market_price setter and before them for people with the same price
    temp_count1 = Count
    while(temp_count1>=0 and sorted_data_list[temp_count1][2] == market_price):
        sorted_data_list[temp_count1][3] = False
        partially_cleared.append(sorted_data_list[temp_count1])
        quantity_partially_cleared += sorted_data_list[temp_count1][2]
        temp_count1-=1
        if(temp_count1 <0):
            break

        #check after the market price setter for people with the same price
    temp_count2 = Count+1
    if(temp_count2 < Size):
        while(temp_count2<=Size and sorted_data_list[temp_count2][2] == market_price):
            partially_cleared.append(sorted_data_list[temp_count2])
            #quantity_partially_cleared += sorted_data_list[temp_count2][1]
            temp_count2+=1
            if(temp_count2 == len(sorted_data_list)):
                break


    ###############################
    #DEFINE THE PROFITS
    ###############################

    #Define profits for the partially Cleared
            #randomly give the quantity to partially cleared, if their quantity is filled then pick another person
    
    indexes_left = [i for i in range(len(partially_cleared))]
    while(quantity_partially_cleared>0):
        index = random.choice(indexes_left)
        if(quantity_partially_cleared > partially_cleared[index][2]):
            for x in data_list:
                if(x.name == partially_cleared[index][0]):
                    x.profit += float((market_price - x.asset[1])*partially_cleared[index][2])
            quantity_partially_cleared -= partially_cleared[index][1]
        else:
            for x in data_list:
                if(x.name == partially_cleared[index][0]):
                    x.profit += float((market_price - x.asset[1])*quantity_partially_cleared)
                quantity_partially_cleared = 0
        
        indexes_left.remove(index)
    
    #Define Profits for the cleared
    for dat in sorted_data_list:
        if (dat[3]):
            for x in data_list:
                if(x.name == dat[0]):
                        x.profit += float(market_price - dat[2])*dat[1]
    
    #Profits for others defaults to zero
  
    return market_price

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
def update_history(data_list):
    for temp in (data_list):
        (temp.hist).append(temp.profit)





# ids = []
starting_units = int(input("Enter the number of units each player starts with: "))
Demand = int(input("Enter the demand for this round: "))
market_cap = int(input("Enter the Market Cap: "))
print(" ")

players, ids = define_players(starting_units)
print(ids)
get_bids(players, market_cap)

sorted_quantities = []
for i in players:
    Len = len(i.quantity)
    for j in range (Len):
        sorted_quantities.append([i.name, i.quantity[j], i.price[j], False])

sorted_quantities = sorted(sorted_quantities, key=lambda x: x[1])
market_price = players_profits(Demand, sorted_quantities, players)

for x in players:
    print(f"profits for {x.name}: {x.profit}")

players = [x for x in players if x.profit != 0]
print(f"if you are bankrupt, you are being kicked out :(")

ids = [x.name for x in players]
print(f"players left {ids}")

print_results(Demand, market_price, players)
update_history(players)
