import json
import sys
from datetime import date, time
from minizinc import Instance, Model, Solver


def encode_time(t):
    # encode a time as an integer for use by the model
    return t.hour*60 + t.minute


def decode_time(t):
    # decode a time encoded as an integer to HH:MM format
    return f'{(t // 60):02d}:{(t % 60):02d}'


def encode_flt(flt):
    # encode a flight in a form required by the model
    flt['preferred'] = encode_time(time.fromisoformat(flt['preferred']))
    flt['earliest'] = encode_time(time.fromisoformat(flt['earliest']))
    flt['latest'] = encode_time(time.fromisoformat(flt['latest']))
    flt['rwy'] = {runways.index(r)+1 for r in flt['rwy']}
    return flt


# load airport data
root = f'data/tmi{sys.argv[1]}'
with open(f'{root}/airport.json', 'r') as file:
    airports = json.load(file)

# load TMI configuration
with open(f'{root}/tmi-config.json', 'r') as file:
    config = json.load(file)
airport = config['airport']
dt = date.fromisoformat(config['date'])
start = time.fromisoformat(config['start'])
config['start'] = encode_time(start)
end = time.fromisoformat(config['end'])
config['end'] = encode_time(end)
del config['airport']
del config['date']
runways = airports[airport]['runway']

# load flight data
with open(f'{root}/flight.json', 'r') as file:
    flight = json.load(file)
fids = list(flight.keys())
flights = [encode_flt(f) for f in list(flight.values())]

# initialise the input data and run the solver
model = Model('./tmi.mzn')
solver = Solver.lookup('gecode')
instance = Instance(solver, model)
instance["num_runways"] = len(runways)
instance["config"] = config
instance["flights"] = flights
result = instance.solve()

# output the results
print(f'TMI Schedule for {airport} on {dt}')
print(f'Commences: {start.strftime("%H:%M")}, Ends: {end.strftime("%H:%M")}')
slot = result['slot']
runway = result['rwy']
res = sorted([(i, slot[i], runway[i]) for i in range(len(slot))
              if slot[i] is not None], key=lambda x: x[1])
for r in res:
    print(f'  {fids[r[0]].ljust(8)}: {decode_time(r[1])} - {runways[r[2]-1]}')
found = False
for i in range(len(slot)):
    if slot[i] is None:
        if not found:
            found = True
            print("Excluded:", end="")
        print(f' {fids[i]}')
print(f'Cost: {result['cost']}')