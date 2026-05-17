% Run with Chuffed or Huub solver for best performance.
% The model gets very expensive very quickly as the data size grows.

include "globals.mzn";

/*
  Parameters
*/

% A TMI runs over a period of no more than a few hours on one day, so 24 hours is adequate for
% modelling. A time is represented as the number of minutes since midnight.
int:  maxtime = 24 * 60;
set of int: TIME = 0..maxtime-1;

% Configuration information required to run a TMI.
type TMI_config = record(
                      TIME: start,             % TMI commences
                      TIME: end,               % TMI finishes
                      array[int] of int: rate  % The rate of each runway
                                               % The minimum duration between consecutive takeoffs
                  );

% The TMI configuration.
TMI_config: config;

% Subset of times over which the TMI runs; slot times must be in this range.
set of int: TMI_TIME = config.start..config.end;

% Filter factor; reduces the size of the flight takeoff windows; a percentage value.
0..100: filter;

% The runways at the airport that are available during the TMI.
% Each runway is represented by a unique integer.
int: num_runways = length(config.rate);
set of int: RUNWAY = 1..num_runways;

% Information on a flight that requires a slot in the TMI.
type flight_info = record(
                       TIME: preferred,    % preferred takeoff time
                       TIME: earliest,     % earliest possible takeoff time
                       TIME: latest,       % latest possible takeoff time
                       set of RUNWAY: rwy  % available runways the flight can use
                   );

% The flights participating in the TMI. Each flight is represented by a unique integer.
list of flight_info: flights;
set of int: FLIGHT = 1..length(flights);

% The flight takeoff windows, reduced by the 'filter' parameter: (earliest,latest).
array[FLIGHT] of tuple(TIME,TIME): window =
     [ let {flight_info: flt = flights[f]; TIME: pref = flt.preferred }
       in (flt.earliest+round((pref-flt.earliest)*filter/100),
           flt.latest-round((flt.latest-pref)*filter/100))
     | f in FLIGHT];

% The period of time a flight's (possibly reduced) takeoff window overlaps the TMI period.
function set of TMI_TIME: overlap(FLIGHT: f) =
     max(config.start,window[f].1)..min(config.end,window[f].2);

% Number of candidates for slot allocation, including empty slot if flight excluded.
int: num_candidates = length([1|f in FLIGHT, r in flights[f].rwy, t in overlap(f)]) + card(FLIGHT);
set of int: CANDIDATE = 1..num_candidates;

% All possible flight runway/takeoff times entailed by the input parameters.
array[CANDIDATE,1..3] of int: candidates =
     array2d(CANDIDATE, 1..3,
             [ [f,r,t][col]
             | f in FLIGHT, r in flights[f].rwy, t in overlap(f), col in 1..3]
             ++ [[f,-1,-1][col] | f in FLIGHT, col in 1..3]);

/*
  Validate the input data.
*/

% Flight times are consistent.
constraint forall(f in FLIGHT)
                 (let {flight_info: fi = flights[f] }
                  in assert(fi.preferred in fi.earliest..fi.latest,
                            "Preferred time (\(fi.preferred)) is not in window for flight '\(f)'")
                  /\ assert(overlap(f) != {},
                            "Window for flight '\(f)' does not overlap TMI period"));

/*
  Decision variables
*/

% Runway and time allocated to each flight:
% - each row contains an identifier/runway/takeoff time triple for a flight
array[FLIGHT,1..3] of var -1..config.end: schedule;

% The set of flights allocated to each runway.
array[RUNWAY] of var set of FLIGHT: runway_allocation =
     [ {f | f in FLIGHT where schedule[f,2] = r} | r in RUNWAY];

/*
  Constraints
*/

% Slot allocated to a flight drawn from the 'candidates' table.
constraint forall(f in FLIGHT)(schedule[f,1] = f /\ table(schedule[f,1..3],candidates));

% Two flights allocated the same runway must depart at least the 'rate' duration apart.
constraint forall(r in RUNWAY, f, g in runway_allocation[r] where f < g)
                 (abs(schedule[f,3]-schedule[g,3]) >= config.rate[schedule[f,2]]);

/*
  Objective
*/


% The cost of a TMI is the sum of:
% - for each flight allocated a slot, the difference between its preferred time and allocated time;
% - if not allocated a slot, the overlap between the flight's takeoff window and the TMI period.
var int: cost;
constraint cost = sum(f in FLIGHT)(if schedule[f,2] = -1
                                   then card(overlap(f))
                                   else abs(flights[f].preferred - schedule[f,3])
                                   endif);

% The goal is to minimize the cost of the TMI.
solve minimize cost;
