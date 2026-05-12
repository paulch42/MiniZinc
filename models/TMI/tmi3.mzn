% Run with Chuffed solver for best performance.
% The model gets very expensive very quickly as the data size grows.

include "globals.mzn";

/*
  Parameters
*/

% A TMI runs over a period of no more than a few hours on one day, so 24 hours is adequate for modelling.
% A time is represented as the number of minutes since midnight.
int:  maxtime = 24 * 60;
set of int: TIME = 0..maxtime-1;

% Subset of times over which the TMI runs; slot times must be in this range.
set of int: TMI_TIME = config.start..config.end;

% The maximum time (in minutes) the TMI enforces between two consecutive takeoffs.
int: max_separation = 15;

% Configuration information required to run a TMI.
type TMI_config = record(
                      TIME: start,  % TMI commences
                      TIME: end,    % TMI finishes
                      array[int] of 1..max_separation: rate
                                    % The rate of each runway - the minimum duration between consecutive takeoffs.
                  );

% The TMI configuration.
TMI_config: config;

% The runways at the airport that are available during the TMI. Each runway is represented by a unique integer.
int: num_runways = length(config.rate);
set of int: RUNWAY = 1..num_runways;

% Information on a flight that requires a slot in the TMI.
type flight_info = record(
                       TIME: preferred,    % preferred takeoff time
                       TIME: earliest,     % earliest possible takeoff time
                       TIME: latest,       % latest possible takeoff time
                       set of RUNWAY: rwy
                   );

% The flights participating in the TMI. Each flight is represented by a unique integer.
list of flight_info: flights;
set of int: FLIGHT = 1..length(flights);

% All possible flight runway/takeoff times within the configuration parameters.
array[int,1..3] of -1..config.end: candidates;

/*
  Validate the input data.
*/

% Flight times are consistent.
constraint forall(f in FLIGHT)(let {flight_info: fi = flights[f] }
                               in assert(fi.preferred in fi.earliest..fi.latest,
                                         "Preferred time (\(fi.preferred)) is not in window for flight '\(f)'") /\
                                  assert(fi.earliest..fi.latest intersect TMI_TIME != {},
                                         "Window for flight '\(f)' does not overlap TMI period"));

% 'candidates' table is consistent.
constraint forall(i in index_set_1of2(candidates))
                 (assert(candidates[i,1] in FLIGHT /\
                         candidates[i,2] in RUNWAY union {-1} /\
                         candidates[i,3] in TMI_TIME union {-1} /\
                         (candidates[i,2] = -1 <-> candidates[i,3] = -1),
                         "Invalid candidate entry: [\(candidates[i,1]),\(candidates[i,2]),\(candidates[i,3])]"));

/*
  Decision variables
*/

% Runway and time allocated to each flight.
array[FLIGHT,1..3] of var -1..config.end: schedule;

/*
  Constraints
*/

% Slot allocated to a flight drawn from the 'candidates' table.
constraint forall(f in FLIGHT)(schedule[f,1] = f /\ table(schedule[f,1..3],candidates));

% Two flights allocated the same runway must depart at least the 'rate' duration apart.
constraint forall(f, g in FLIGHT where f < g /\ schedule[f,2] != -1 /\ schedule[f,2] = schedule[g,2])
                 (abs(schedule[f,3]-schedule[g,3]) >= config.rate[schedule[f,2]]);

/*
  Objective
*/

% The length of time a flight's takeoff window overlaps the TMI period.
function var int: overlap(FLIGHT: f) = min(config.end,flights[f].latest) - max(config.start,flights[f].earliest);

% The cost of a TMI is the sum of:
% - for each flight allocated a slot, the difference between its preferred time and allocated time;
% - for a flight not allocated a slot, the overlap between the flight's takeoff window and the TMI period.
var int: cost;
constraint cost = sum(f in FLIGHT)(if schedule[f,2] = -1 then overlap(f) else abs(flights[f].preferred - schedule[f,3]) endif);

% The goal is to minimize the cost of the TMI.
solve minimize cost;