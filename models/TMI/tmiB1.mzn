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

% Configuration information required to run a TMI.
type TMI_config = record(
                      TIME: start,             % TMI commences
                      TIME: end,               % TMI finishes
                      array[int] of int: rate  % The rate of each runway
                                               % The minimum duration between consecutive takeoffs
                  );

% The TMI configuration.
TMI_config: config;

% The runways at the airport that are available during the TMI. Each runway is represented by a unique integer.
int: num_runways = length(config.rate);
set of int: RUNWAY = 1..num_runways;

% Information on a flight that requires a slot in the TMI.
type flight_info = record(
                       TIME: preferred,  % preferred takeoff time
                       TIME: earliest,   % earliest possible takeoff time
                       TIME: latest      % latest possible takeoff time
                   );

% The flights participating in the TMI. Each flight is represented by a unique integer.
list of flight_info: flights;
set of int: FLIGHT = 1..length(flights);

% The interval a flight's takeoff window overlaps the TMI period (derived).
array[FLIGHT] of set of TMI_TIME: overlap = [max(config.start,flights[f].earliest)..min(config.end,flights[f].latest) | f in FLIGHT];

% All possible flight runway/takeoff times for all flights.
array[int,1..3] of int: candidates;

/*
  Validate the input data.
*/

% Flight times are consistent.
constraint forall(f in FLIGHT)
                 (let {flight_info: fi = flights[f] }
                  in assert(fi.preferred in fi.earliest..fi.latest,
                            "Preferred time (\(fi.preferred)) is not in window for flight '\(f)'")
                  /\ assert(overlap[f] != {},
                            "Window for flight '\(f)' does not overlap TMI period"));

% 'candidates' table is consistent.
constraint forall(i in index_set_1of2(candidates))
                 (assert(candidates[i,1] in FLIGHT /\
                         candidates[i,2] in RUNWAY union {-1} /\
                         candidates[i,3] in TMI_TIME union {-1} /\
                         (candidates[i,2] = -1 <-> candidates[i,3] = -1),
                         "Invalid candidate: \(candidates[i,1..3])"));

/*
  Decision variables
*/

% Runway and time allocated to each flight:
% - each row contains an identifier/runway/takeoff time triple for a flight
array[FLIGHT,1..3] of var -1..config.end: schedule;

% The set of flights allocated to each runway.
% array[RUNWAY] of var set of FLIGHT: runway_allocation =
%      [ {f | f in FLIGHT where schedule[f,2] = r} | r in RUNWAY];


/*
  Constraints
*/

% Slot allocated to a flight drawn from the 'candidates' table.
constraint forall(f in FLIGHT)(schedule[f,1] = f /\ table(schedule[f,1..3],candidates));

% Two flights allocated the same runway must depart at least the 'rate' duration apart.
% constraint forall(r in RUNWAY, f, g in runway_allocation[r] where f < g)
%                  (abs(schedule[f,3]-schedule[g,3]) >= config.rate[schedule[f,2]]);
constraint forall(f, g in FLIGHT where f < g /\ schedule[f,2] != -1 /\ schedule[f,2] = schedule[g,2])
                 (abs(schedule[f,3]-schedule[g,3]) >= config.rate[schedule[f,2]]);

% The construction of the 'candidates' table ensures:
% - A flight is allocated a runway it is able to use.
% - The time allocated to a flight falls within its takeoff window and the TMI period.
% - A priority flight is allocated a slot.

/*
  Objective
*/

% The cost of a TMI is the sum of:
% - for each flight allocated a slot, the difference between its preferred time and allocated time;
% - if not allocated a slot, the overlap between the flight's takeoff window and the TMI period.
var int: cost;
constraint cost = sum(f in FLIGHT)(if schedule[f,2] = -1
                                   then card(overlap[f])
                                   else abs(flights[f].preferred - schedule[f,3])
                                   endif);

% The goal is to minimize the cost of the TMI.
solve minimize cost;