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

There are two variants of the model:
- [tmi-standalone](tmi-standalone.mzn) has more expressive input data, incorporating strings and enums, that is easier to interpret. It also provides meaningful output.
- [tmi](tmi.mzn) is a bare bone model in that everything is represented as integers, and decision variables are output in default MiniZinc format.

The latter model was designed to be invoked from the P{ython script [tmi.py](tmi.py). The input to the Python script is a set of three JSON files, and the output is pretty-printed by Python.

To run the script:
```
python3 tmi.py <n>
```
where \<n> is a digit corresponding to one of the folders in [data](data) (e.g. _1_ for _tmi1_).

Also in [data](data), _data1.dzn_ and _data2.dzn_ are direct input for _tmi.mzn_, and _data1s.dzn_ and _data2s.dzn_ are input for _tmi_standalone.mzn_.