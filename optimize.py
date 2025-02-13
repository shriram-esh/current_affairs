import numpy as np
from scipy.optimize import minimize

'''

'x' refers to the # of units bid
'c' refers to cost to bid the units

Objective function: 
    min c1*x1 + c2*x2 + c3*x3 

Constraints:
s.t.
    x1 + x2 + x3 = d
    0 <= x1 <= x1_bar 
    0 <= x2 <= x2_bar 
    0 <= x3 <= x3_bar 

'''

class MarketRound:

    def __init__(self, bids, quantity, demand):

        # Error Check
        if not isinstance(bids, list) or not isinstance(quantity, list) or not isinstance(demand, (int, float)):
            raise TypeError("Both 'bids' and 'quantity' must be 'lists'. Also 'demand' must be an 'int' or 'float'")

        if not all(isinstance(bid, (int, float)) for bid in bids):
            raise TypeError("All elements of 'bids' must be 'int' or 'float'")
        if not all(isinstance(q, (int, float)) for q in quantity):
            raise TypeError("All elements of 'quantity' must be 'int' or 'float'")
        
        if len(bids) != len(quantity):
            raise ValueError("'bids' and 'quantity' lengths don't match")
        
        if demand < 0:
            raise ValueError("'demand' must be a positive or zero")
        
        if not bids or not quantity:
            raise ValueError("'bids' and 'quantity' lengths must be nonzero")

        bounds = []
        for q in quantity:
            bounds.append((0, q))
        
        constraints = [{'type': 'eq', 'fun': self.equality_constraint}]

        initial = []
        for i in range(len(bounds)):
            mid_value = (bounds[i][0] + bounds[i][1]) / 2
            initial.append(mid_value)
        
        self.bids = bids
        self.bounds = bounds
        self.constraints = constraints
        self.demand = demand
        self.initial = initial

    def objective_fcn(self, x):
        market_entry = 0

        for index, quantity in enumerate(x):
            market_entry += self.bids[index] * quantity

        return market_entry

    def equality_constraint(self, x):
        supply = 0

        for s in x:
            supply += s
        
        return supply - self.demand  # Set up of constraints requires everything to be "= 0"
    
    def get_result(self):
        '''
        Parameters for minimize function are as follows:
            fun - objective function to be minimized
            x0 = ndarry of initial guess
            method - type of solver
            bounds = bounds on variables
            constraints - list of constraint

            Note* SLSQP for the 'method' is a good choice for solving an equality and inequality constraint.
        '''

        result = minimize(self.objective_fcn, self.initial, method='SLSQP', bounds=self.bounds, constraints=self.constraints)
        return np.round(result['x'], decimals=0)