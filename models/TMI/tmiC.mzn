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
                      TIME: start,  % TMI commences
                      TIME: end     % TMI finishes
                  );

% The TMI configuration.
TMI_config: config;

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

% Range of values that can be assigned by solver.
set of int: RANGE = -1..config.end;

% All possible slots for all flights.
array[int,1..4] of int: candidates;

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
                 (assert(candidates[i,2] in FLIGHT /\
                         (candidates[i,3] = -1 <-> candidates[i,4] = -1),
                         "Invalid candidate: \(candidates[i,1..4])"));

/*
  Decision variables
*/

% Runway and time allocated to each flight:
% - each row contains an key/flight id/runway/takeoff time quadruple for a flight
array[FLIGHT,1..4] of var RANGE: schedule;

/*
  Constraints
*/

% Slot allocated to a flight drawn from the 'candidates' table.
constraint forall(f in FLIGHT)(schedule[f,2] = f /\ table(schedule[f,1..4],candidates));

% No slot allocated to more than one flight.
constraint all_different([schedule[f,1] | f in FLIGHT],{0});

% The construction of the 'candidates' table ensures:
% - A flight is allocated a runway it is able to use.
% - The time allocated to a flight falls within its takeoff window and the TMI period.
% - A priority flight is allocated a slot.
% - Two flights allocated the same runway depart at different times.

/*
  Objective
*/

% The cost of a TMI is the sum of:
% - for each flight allocated a slot, the difference between its preferred time and allocated time;
% - if not allocated a slot, the overlap between the flight's takeoff window and the TMI period.
var int: cost;
constraint cost = sum(f in FLIGHT)(if schedule[f,3] = -1
                                   then card(overlap[f])
                                   else abs(flights[f].preferred - schedule[f,4])
                                   endif);

% The goal is to minimize the cost of the TMI.
solve minimize cost;