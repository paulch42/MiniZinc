import json
import sys
from minizinc import Instance, Model, Solver
from datetime import timedelta

# load teams data
model_root = f'league{sys.argv[1]}'
data_root = f'data/league{sys.argv[2]}'
with open(f'{data_root}.json', 'r') as file:
    config = json.load(file)
teams = config['teams']

# initialise the input data and run the solver
model = Model(f'./{model_root}.mzn')
solver = Solver.lookup('huub')
instance = Instance(solver, model)
instance['num_teams'] = len(teams)
co_home = []
for p in config['co_home']:
    co_home.append([teams.index(p[0])+1, teams.index(p[1])+1])
instance['co_home'] = co_home
try:
    result = instance.solve(intermediate_solutions=True,
                            time_limit=timedelta(minutes=10))
except AssertionError as e:
    print(e)
    exit(0)
    
if not result:
    print('Unsatisfiable')
    exit(0)

# output the results
print('League Schedule\n')
schedule = result[-1].schedule
for i, round in enumerate(schedule):
    print(f'Round {i+1}')
    plays = set()
    for match in round:
        print(f'    {teams[match[0]-1]} - {teams[match[1]-1]}')
        plays.add(match[0]-1)
        plays.add(match[1]-1)
    bye = set(range(len(teams))) - plays
    if bye:
        print(f'    Bye: {teams[bye.pop()]}')
if hasattr(result[-1], 'cost'):
    print(f'\nCost: {result[-1].cost}')
