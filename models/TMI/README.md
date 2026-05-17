# Traffic Management Initiative

A Traffic Management Initiative (TMI) is employed to manage aeronautical resources. One kind of TMI is to allocate slots (takeoff times) to departing aircraft at an airport to avoid congestion and ensure fair access.

This model is a simplified version of a TMI that applies a small (but non-trivial) set of rules.

Input:
- Details of the aircraft that wish to depart during the TMI.
- Details of the airport at which the TMI is run.
- Details that are specific to the TMI and the time at which it occurs.

Constraints:
- Specified flights wish to depart an airport.
  - The flights that plan to depart during the period of the TMI.
- Each flight may only take off from certain runways.
  - Larger aircraft may not be able to take off from shorter runways.
- Each flight has a preferred take off time.
  - The time the aircraft operator would ideally like their flight to depart.
- Each flight must take off in a nominated time window.
  - Aircraft operators have schedules to meet; the allocated take off time must not be too far from the scheduled time.
- Only certain runways are available.
  - The configuration of resources dictates which of the runways at an airport are available for use.
- Each runway has a maximum rate at which departures can occur.
  - The rates may differ for different runways. Rate is impacted by factors such as the predicted weather and airport noise restrictions.
- The TMI occurs over a fixed interval.
  - A TMI need only run at times when there is likely to be competition for resources.

Given these inputs and constraints:
- Allocate a runway and take off time to as many flights as possible such that the constraints are satisfied. Flights should be allocated a slot as close as possible to their preferred takeoff time.

There are four variants of the model, exploring different approaches.

## Model 1
[tmi1.mzn](tmi1.mzn) is a standalone  model that takes input from a MiniZinc data file and employs strings and enum to aid comprehension of the model and data. A formatted solution is output.

Data files [tmi1-1.dzn](data/tmi1-1.dzn) and [tmi1-2.dzn](data/tmi1-2.dzn) are example inputs that can be run from the command line or IDE. Example output for [tmi1-1.dzn](data/tmi1-1.dzn):
```
Schedule for TMI YSSY260123:
    QFA1   : 00:25 - R34L
    VOZ42  : 00:35 - R25
excluded: JST666 
cost: 3
```

## Model 2

[tmi2.mzn](tmi2.mzn) is a more bare bones model in that everything is represented as an integer, and decision variables are output in default MiniZinc format.
The model is intended to be invoked from the Python script [tmi2.py](tmi2.py) that reads a collection of JSON formatted input files and converts the data to a form suitable for the [MiniZinc Python](https://pypi.org/project/minizinc/) package to pass to [tmi2.mzn](tmi2.mzn). Run the model with
```
python3 tmi2.py <n>
```
where \<n> is a digit corresponding to one of the folders in [data](data) (e.g. _1_ for _tmi1_). These folders contain the JSON files.

The output is pretty printed by Python.

Data files [tmi2-1.dzn](data/tmi2-1.dzn) and [tmi2-2.dzn](data/tmi2-2.dzn) are example inputs that can be run from the command line or IDE, hence are equivalent to the data [tmi2.mzn](tmi2.mzn) generates and feeds to the [MiniZinc Python](https://pypi.org/project/minizinc/) interface.

Example output for [tmi3](data/tmi3):
```
TMI Schedule for YSSY on 2026-03-25
Commences: 08:00, Ends: 08:30
  ANZ248  : 08:02 - 16L
  TMN21   : 08:02 - 16R
  JST611  : 08:05 - 16R
  JST822  : 08:06 - 16L
  QFA139  : 08:08 - 16R
  VOZ882  : 08:10 - 16L
  RXA6783 : 08:11 - 16R
  VOZ981  : 08:14 - 16R
  QLK34D  : 08:14 - 16L
  ANZ224  : 08:17 - 16R
  QLK227D : 08:18 - 16L
  VOZ973  : 08:20 - 16R
  QFA487  : 08:22 - 16L
  QLK209D : 08:23 - 16R
  VOZ670  : 08:26 - 16R
  QLK166D : 08:28 - 16L
  QLK108D : 08:30 - 16R
Excluded:
  QFA477
  QFA485
Cost: 13
```
## Model 3

[tmi3.mzn](tmi3.mzn) takes a different modelling approach. The first two models specify the problem constraints directly. This model generates a collection of all possible candidate slot allocations entailed by the input parameters, based on the same set of JSON files used by Model 2. The candidates then serve as the values for the global constraint [table](https://docs.minizinc.dev/en/stable/lib-globals-extensional.html). Running the model is similar to model 2:
```
python3 tmi3.py <n>
```
The output is pretty-printed by Python.

Data files [tmi3-1.dzn](data/tmi3-1.dzn) and [tmi3-2.dzn](data/tmi3-2.dzn) are example inputs that can be run from the command line or IDE, hence are equivalent to the data [tmi3.mzn](tmi3.mzn) generates and feeds to the [MiniZinc Python](https://pypi.org/project/minizinc/) interface. In particular, these files demonstrate how the table of candidates is constructed.

Example output for [tmi6](data/tmi6):
```
TMI Schedule for YSSY on 2026-03-25
Commences: 08:00, Ends: 08:20
Runway: 16L
  TMN21   : 08:01
  JST822  : 08:07
  VOZ981  : 08:13
  QLK34D  : 08:19
Runway: 16R
  ANZ248  : 08:00
  JST611  : 08:04
  QFA139  : 08:08
  VOZ882  : 08:12
  QLK227D : 08:16
  VOZ973  : 08:20
Excluded:
  QFA477
  RXA6783
  ANZ224
Cost: 32
```
All models calculate optimal solutions, but complexity is exponential so solution time quickly becomes impractial. Each flight specifies a takeoff window during which it is willing to depart. The narrower the window, the quicker the solution time as less searching needs to occur. [tmi3.mzn](tmi3.mzn) allows an extra parameter, such as:
```
python3 tmi3.py <n> 50
```
which means run the model with the input data but reduce the size of the takeoff window by 50% with respect to the input file. There is a consequent decrease in the table of candidates, and hence solution time. However, while the model will calculate the optimal solution for the data it is given, the pre-processing of the input data means a sub-optimal solution with respect to the original data may result. The higher the value, the more likely the solution is sub-optimal. A value of 0 means no reduction (equivalent to omitting the argument); a value of 100 means a flight can only be allocated its preferred time.

## Model 4

[tmi4.mzn](tmi4.mzn) takes the same approach as [tmi3.mzn](tmi3.mzn) but in this case the generation (and reduction) of the candidate table of is carried out by MiniZinc rather than Python.

Like Model 3, Model 4 allows an extra parameter to reduce the size of the takeoff windows.

## Performance Comparison

The table below is a performance comparison of models 2, 3 and 4 using data sets 3 through 6. All times are for the Chuffed solver in _minutes:seconds_. Running on a M2 MacBook Air with 24GB RAM.

|Data Set |Model 2|Model 3|Model 4|
|---------|-------|-------|-------|
|3|00:08|00:06|00:05|
|4|00:15|00:19|00:16|
|5|15:11|03:41|03:00|
|6|31:37|14:45|16:23|

The table below is a performance comparison of model 4 with different window reduction values on data set 6.

|Reduction|Time|Cost|
|---------|-------|-------|
|0%|16:23|19|
|40%|12:04|21|
|50%|03:34|22|
|60%|02:32|22||
|70%|01:47|26||
|80%|00:59|37|
|90%|00:10|55|
|100%|00:07|104|

The results clearly demonstrate the effect the window size has on performance and quality of solution.