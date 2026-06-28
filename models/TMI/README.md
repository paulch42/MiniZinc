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
- Each flight may only takeoff from certain runways.
  - Larger aircraft may not be able to takeoff from shorter runways.
- Each flight has a preferred takeoff time.
  - The time the aircraft operator would ideally like their flight to depart.
- Each flight must takeoff in a nominated time window.
  - Aircraft operators have schedules to meet; the allocated takeoff time must not be too far from the scheduled time.
- A flight flagged as priority must be allocated a slot.
  - Medical flights, head of state, etc.
- Only certain runways are available.
  - The configuration of resources dictates which of the runways at an airport are available for use.
- Each runway has a maximum rate at which departures can occur.
  - The rates may differ for different runways. Rate is impacted by factors such as the predicted weather and airport noise restrictions.
- The TMI occurs over a fixed interval.
  - A TMI need only run at times when there is likely to be competition for resources.

Given these inputs and constraints:
- Allocate a runway and takeoff time to as many flights as possible such that the constraints are satisfied. Flights should be allocated a slot as close as possible to their preferred takeoff time.

There are multiple variants of the model, exploring different approaches.

## Approach A

Approach A is direct in that the data and constraints closely reflect the requirements and the structure of the domain data.

### Model 1
[tmiA1.mzn](tmiA1.mzn) is a standalone  model that takes input from a MiniZinc data file and employs strings and enums to aid comprehension of the model and data. A formatted solution is output.

Data files [tmiA1-1.dzn](data/tmiA1-1.dzn) and [tmiA1-2.dzn](data/tmiA1-2.dzn) are example inputs that can be run from the command line or IDE. Example output for [tmiA1-1.dzn](data/tmiA1-1.dzn):
```
Schedule for TMI YSSY260123:
    QFA1   : 00:25 - R34L
    VOZ42  : 00:35 - R25
excluded: JST666 
cost: 4
```

### Model 2

[tmiA2.mzn](tmiA2.mzn) is a more bare bones model in that everything is represented as an integer, and decision variables are output in default MiniZinc format.
The model is intended to be invoked from the Python script [tmiA2.py](tmiA2.py) that reads a collection of JSON formatted input files (such as [tmi1](data/tmi1)) and converts the data to a form suitable for the [MiniZinc Python](https://pypi.org/project/minizinc/) package to pass to [tmiA2.mzn](tmiA2.mzn). Run the model with:
```
python3 tmiA2.py <n>
```
where \<n> is a digit corresponding to one of the folders in [data](data) (e.g. _1_ for _tmi1_). These folders contain the JSON files.

The output is pretty printed by Python.

Data files [tmiA2-1.dzn](data/tmiA2-1.dzn) and [tmiA2-2.dzn](data/tmiA2-2.dzn) are example inputs that can be run from the command line or IDE, hence are equivalent to the data [tmiA2.py](tmiA2.py) generates and feeds to the [MiniZinc Python](https://pypi.org/project/minizinc/) interface.

Example output for [tmi3](data/tmi3):
```
TMI Schedule for YSSY on 2026-03-25
Commences: 08:00, Ends: 08:20
  QFA139  : 08:00 - 16R
  ANZ248  : 08:01 - 16L
  JST611  : 08:04 - 16R
  JST822  : 08:07 - 16L
  VOZ882  : 08:08 - 16R
  RXA6783 : 08:12 - 16R
  VOZ981  : 08:13 - 16L
  QLK34D  : 08:16 - 16R
  QLK227D : 08:19 - 16L
  VOZ973  : 08:20 - 16R
Excluded:
  TMN21
  QFA477
  ANZ224
Cost: 34
```
## Approach B

The first approach specifies the problem constraints directly. This approach generates a collection of all possible candidate slot allocations entailed by the input parameters, based on the same set of JSON files used by Model A2. The candidates then serve as the values for the global constraint [table](https://docs.minizinc.dev/en/stable/lib-globals-extensional.html).

### Model 1

The model is implemented by [tmiB1.mzn](tmiB1.mzn) and its characteristic is exemplified in data file [tmiB1-1.dzn](data/tmiB1-1.dzn). In particular, table _candidates_ is a list of triples representing flight identifier, runway and slot time. There is a row in the table for each possible slot of each flight, taking account of:
- the TMI period;
- the flight takeoff window;
- the runways available in the TMI;
- the runways the flight can use;
- .

The granularity is one minute. That is, every minute is considered a potential slot time for a flight. 

To run the model:
```
python3 tmiB1.py <n>
```
The output is pretty-printed by Python.

Data files [tmiB1-1.dzn](data/tmiB1-1.dzn) and [tmiB1-2.dzn](data/tmiB1-2.dzn) are example inputs that can be run from the command line or IDE, hence are equivalent to the data [tmiB1.py](tmiB1.py) generates and feeds to the [MiniZinc Python](https://pypi.org/project/minizinc/) interface, demonstrating how the table of candidates is constructed.

Example output for [tmi4](data/tmi4):
```
TMI Schedule for YSSY on 2026-03-25
Commences: 08:00, Ends: 08:30
Runway: 16L
  TMN21   : 08:01
  JST611  : 08:05
  VOZ882  : 08:09
  VOZ981  : 08:13
  QLK227D : 08:17
  QFA485  : 08:21
  QLK209D : 08:25
  QLK108D : 08:30
Runway: 16R
  ANZ248  : 08:02
  JST822  : 08:05
  QFA139  : 08:08
  RXA6783 : 08:11
  QLK34D  : 08:14
  ANZ224  : 08:17
  VOZ973  : 08:20
  QFA487  : 08:23
  VOZ670  : 08:26
  QLK166D : 08:29
Excluded:
  QFA477
Cost: 17
```
All models calculate optimal solutions, but complexity is exponential so solution time quickly becomes impractial. Each flight specifies a takeoff window during which it is willing to depart. The narrower the window, the quicker the solution time as there are fewer candidate slots hence less searching needs to occur. [tmiB1.mzn](tmiB1.mzn) allows an extra parameter, such as:
```
python3 tmi3.py <n> 50
```
which means run the model with the input data but reduce the size of the takeoff window by 50% with respect to the input file. There is a consequent decrease in the table of candidates, and hence solution time. However, while the model will calculate the optimal solution for the data it is given, the pre-processing of the input data means a sub-optimal solution with respect to the original data may result. The higher the value, the more likely the solution is sub-optimal. A value of 0 means no reduction (equivalent to omitting the argument); a value of 100 means a flight can only be allocated its preferred time.

### Model 2

[tmiB2.mzn](tmiB2.mzn) takes the same approach as [tmiB1.mzn](tmiB1.mzn) but in this case the generation (and percentage reduction) of the candidate table is carried out by MiniZinc rather than Python. The input JSON  files are identical in either case. There is simply a different split of the responsibilities allocated to the MiniZinc and Python components.

Like Model B1, Model B2 allows an extra parameter to reduce the size of the takeoff windows.

## Approach C

Approach C is somewhat different from the earlier approaches and is a better reflection of how TMI processing occurs in the aviation industry.

There are two key differences:
- The runways in use and rates can vary over the period of a TMI.
- A fixed set of slots is pre-calculated from the rates rather than allowing any minute to serve as a slot time.

This approach is more flexible in that it allows for a changing runway configuration during the TMI, but less flexible in that the available slots are pre-determined.

The model is [tmiC.mzn](tmiC.mzn). Data files [tmiC-1.dzn](data/tmiC-1.dzn) and [tmiC-2.dzn](data/tmiC-2.dzn) are example inputs that can be run from the command line or IDE, hence are equivalent to the data [tmiC.py](tmiC.py) generates and feeds to the [MiniZinc Python](https://pypi.org/project/minizinc/) interface. The data files are in fact very similar to those of [tmiB1-1.dzn](data/tmiB1-1.dzn) and [tmiB1-2.dzn](data/tmiB1-2.dzn), but there are far fewer entries in the _candidates_ table. ([tmiC-2.dzn](data/tmiC-2.dzn) has 29 entries, whereas [tmiB1-2.dzn](data/tmiB1-2.dzn) has 132 entries.)

## Performance Comparison

The table below is a performance comparison of the models on various data sets. All times are for the Chuffed solver in _minutes:seconds_. Running on a M2 MacBook Air with 24GB RAM.

|Data Set |Model A2|Model B1|Model B2|Model C|
|---------|-------|-------|-------|-------|
|3|00:05|00:04|00:03|00:01|
|4|01:07|00:54|00:38|00:01|
|5|18:38|03:42|03:01|00:02|
|6|41:23|14:14|16:19|00:03|

Approach A is by far the least efficient, which is not surprising since it models directly the requirements and makes no use of global constraints.

Approach B performs somewhat better, but solution time increases significantly as the input data size increases. The improvement in performance is primarily due to the use of the _table_ global constraint, allowing the solver to apply sophisticated search techniques. However, the search space is large for larger data sets and this is reflected in the solution time.

Approach C outperforms the others by a considerable margin. This is due to two factors:
- The fixed slots result in far fewer candidate slots, which significantly reduces the search space when _table_ is invoked. (29 vs 132 entries in the example noted earlier, and this difference will increase with a larger data set.)
- On earlier models the constraint that ensures flights are not allocated a slot that is too close to another flight on the same runway is computationally expensive. This is replaced by the _alldifferent_ global constraint in model C allowing the solver to employ far more efficient techniques.

Note: no search annotations have been specified in any model. There is potential for improvement, particularly on approaches A and B, though they would never reach the level of approach C.

The table below is a performance comparison of model B2 with different window reduction values on data set 6.

|Reduction|Time|Cost|
|---------|-------|-------|
|0%|16:19|19|
|40%|03:39|19|
|50%|01:30|19|
|60%|01:38|19|
|70%|00:17|19|
|80%|00:10|21|
|90%|00:11|47|
|100%|00:05|64|

The results clearly demonstrate the effect the window size has on performance and quality of solution:
- Increased window size has a negative impact on performance reflecting the increased search space.
- Quality increases with increased window size reflecting that more candidate solutions are available for selection.