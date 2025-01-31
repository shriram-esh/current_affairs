#import numpy as np

#defines each bidder
class Data:

    def __init__(self, name, energy_type, bid, quantity, profit, cleared):
        self.name = name #identify the player
        self.energy_type = energy_type
        self.bid = bid #only put reasonable - nonnegative and not greater than 1000
        self.quantity = quantity
        self.profit = profit
        self.cleared =cleared

#GET THIS INFO FROM ELSEWHERE AND DEFINE THESE VARIABLES
num_players = 6     #get this from somewhere else
Demand = 13         #define demand based on historic stuff


##prompt for data input into array
data_list = []
for i in range(num_players):
    temp = Data((input("Please enter your name: ")), input("enter the energy type: "), int(input("Enter the price of your bid: ")), int(input("Enter the quantity of your bid: ")), 0, False)
    data_list.append(temp)
    print("")
print("")

#sort the data so we can go over it in order of the graph
sorted_data_list = sorted(data_list, key=lambda x: x.bid)
Size = len(data_list)
Quantity_Sum=0
Count = 0

#while the total quantity so far is less than the demand, clear the next bidder and their quantity
while(Quantity_Sum<Demand and Count<Size):
    Quantity_Sum += sorted_data_list[Count].quantity
    sorted_data_list[Count].cleared = True
    Count+=1
    
Count-=1 #the bidder at this index of the sorted array defines the market_price from their price
market_price  = sorted_data_list[Count].bid

#all the people bidding at market price are partially in the market
partially_cleared = []

temp_count1 = Count
while(temp_count1>=0 and sorted_data_list[temp_count1].bid == market_price):       #check the market_price setter and before them for people with the same price
    sorted_data_list[temp_count1].cleared = False
    partially_cleared.append(sorted_data_list[temp_count1])
    temp_count1-=1
    if(temp_count1 <0):
        break

temp_count2 = Count+1
if(temp_count2 < Size):
    while(temp_count2<=Size and sorted_data_list[temp_count2].bid == market_price):       #check after the market price setter for people with the same price
        partially_cleared.append(sorted_data_list[temp_count2])
        temp_count2+=1
        if(temp_count2 == len(sorted_data_list)):
            break

#print the Demand and market price 
print("For a demand of: ", end = " ")
print(Demand)
print("The Market price was: ", end=" ")
print(market_price, end='\n\n')


#Say if player is cleared, partially cleared, or out of the market
#if the player is cleared, print thier profit
for dat in sorted_data_list:
    if (dat.cleared):
        dat.profit =(market_price - dat.bid)*dat.quantity
        print(dat.name, end=" ")
        print("'s profit is: ",end="")
        print(dat.profit)
        
    elif (dat in partially_cleared):
        print(dat.name, end=" ")
        print("was partially cleared",end="\n")
        dat.profit=0                                #what should their profit be?

    elif not (dat.cleared):
        print(dat.name, end=" ")
        print("was not cleared",end="\n")
