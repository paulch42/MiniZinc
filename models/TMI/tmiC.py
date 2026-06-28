import json
import sys
from datetime import date, time, timedelta, datetime
from minizinc import Instance, Model, Solver


def encode_time(t):
    # encode a time as an integer for use by the model
    return t.hour*60 + t.minute


def decode_time(t):
    # decode a time encoded as an integer to HH:MM format
    return f'{(t // 60):02d}:{(t % 60):02d}'


def encode_times(id, flt, tmi_date):
    # convert the flight time strings to date/time objects
    try:
        flt['preferred'] = datetime.combine(
            tmi_date, time.fromisoformat(flt['preferred']))
        flt['earliest'] = datetime.combine(
            tmi_date, time.fromisoformat(flt['earliest']))
        flt['latest'] = datetime.combine(
            tmi_date, time.fromisoformat(flt['latest']))
    except Exception as e:
        print(f'Invalid data for "{id}"')
        raise e
    return flt


def encode_flight(f):
    # convert the flight time objects to integers for use by the model
    return {'preferred': encode_time(f['preferred']),
            'earliest': encode_time(f['earliest']),
            'latest': encode_time(f['latest'])}


# load airport data
root = f'data/tmi{sys.argv[1]}'
with open(f'{root}/airport.json', 'r') as file:
    airports = json.load(file)

# load TMI configuration
with open(f'{root}/tmi-config-C.json', 'r') as file:
    config = json.load(file)
airport = config['airport']
runways = airports[airport]['runway']
tmi_date = date.fromisoformat(config['date'])
config['start'] = datetime.combine(
    tmi_date, time.fromisoformat(config['start']))
start = config['start']
config['end'] = datetime.combine(tmi_date, time.fromisoformat(config['end']))
end = config['end']
del config['airport']
del config['date']

# sort and validate the 'rate' elements in the config
rates = sorted(config['rates'], key=lambda x: x['from'])
rates = [{'from': datetime.combine(tmi_date, time.fromisoformat(
    r['from'])), 'rwy': r['rwy']} for r in rates]
if rates[0]['from'] != config['start']:
    print(
        f'First rate ({rates[0]['from']}) does not match TMI start ({config['start']})')
    exit(0)
if rates[-1]['from'] >= config['end']:
    print(
        f'Last rate ({rates[-1]['from']}) is not before end of TMI ({config['end']})')
    exit(0)
rates.append({'from': config['end']})
config['rates'] = rates

# create the available slots
current = {r: config['start'] for r in runways}
slots = {}
slot_id = 1
for i, period in enumerate(rates[:-1]):
    next = rates[i+1]['from']
    for rwy, rate in period['rwy'].items():
        if current[rwy] < period['from']:
            current[rwy] = period['from']
        while current[rwy] < next:
            if rwy in slots:
                slots[rwy].append((slot_id,current[rwy]))
            else:
                slots[rwy] = [(slot_id,current[rwy])]
            slot_id += 1
            current[rwy] += timedelta(minutes=rate)

# load the flight data
with open(f'{root}/flight.json', 'r') as file:
    flight = json.load(file)
for key, value in flight.items():
    encode_times(key, value, tmi_date)

# create the candidate flight slots
candidates = []
for key, value in flight.items():
    num = 0
    for r in value['rwy']:
        if r in slots:
            for (id,tm) in slots[r]:
                if value['earliest'] <= tm and tm <= value['latest']:
                    candidates.append((id, key, r, tm))
                    num += 1
    if not value.get('priority', False):
        candidates.append((0, key, None, None))
        num += 1
    if num == 0:
        print(f'No available slots for {key}')
        exit(0)
    del value['rwy']

# convert data to form accepted by model
fid2index = {fid: index for index, fid in enumerate(list(flight.keys()))}
index2fid = {index: fid for fid, index in fid2index.items()}
rwy2index = {rwy: index for index, rwy in enumerate(runways)}
index2rwy = {index: rwy for rwy, index in rwy2index.items()}
del config['rates']
config['start'] = encode_time(config['start'])
config['end'] = encode_time(config['end'])
flight_model = [encode_flight(flight[index2fid[i]])
                for i in range(len(index2fid))]
candidates = [[id, fid2index[f]+1, rwy2index[r]+1 if r else -1,
               encode_time(t) if t else -1] for (id, f, r, t) in candidates]

# initialise the input data and run the solver
model = Model('./tmiC.mzn')
solver = Solver.lookup('chuffed')
instance = Instance(solver, model)
instance["config"] = config
instance["flights"] = flight_model
instance['candidates'] = candidates
# print(instance['config'])
# print(instance['flights'])
# print(instance['candidates'])
result = instance.solve()
if not result:
    print('No departure schedule satisfies the constraints')
    exit(0)

# output the results
print(f'TMI Schedule for {airport} on {tmi_date}')
print(f'Commences: {start.strftime("%H:%M")}, Ends: {end.strftime("%H:%M")}')
schedule = result['schedule']
for index,rwy in index2rwy.items():
    flts = []
    for [_,fid,r,tkof] in schedule:
        if r-1 == index:
            flts.append((index2fid[fid-1],decode_time(tkof)))
    if flts:
        print(rwy)
        sflts = sorted(flts, key=lambda x: x[1])
        print('\n'.join([f'  {x:8} {y}' for (x,y) in sflts]))
excluded = [index2fid[id-1] for [_,id,rwy,_] in result['schedule'] if rwy == -1]
if excluded:
    print('Excluded:')
    print('\n'.join([f'  {i}' for i in excluded]))
print(f'Cost: {result['cost']}')