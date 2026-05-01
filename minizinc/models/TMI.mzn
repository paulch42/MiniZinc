% A TMI runs over a period of a few hours so 24 hours is adequate for modelling.
% A time is represented as the number of minutes since midnight.
int:  maxtime = 24 * 60;
set of int: TIME = 0..maxtime-1;

% The maximum time (in minutes) the TMI enforces between two consecutive takeoffs.
int: max_separation = 15;

% The runways at the airport. Each runway is represented by a unique integer.
int: num_runways;
set of int: RUNWAY = 1..num_runways;

% Configuration information required to run a TMI.
type TMI_config = record(
                      TIME: start,  % TMI commences
                      TIME: end,    % TMI finishes
                      array[RUNWAY] of opt 1..max_separation: rate
                                    % The rate of each runway - the minimum duration between consecutive takeoffs.
                                    % If <>, indicates the runway is not available during the TMI.
                  );

% The TMI configuration.
TMI_config: config;

% The runways available during the TMI (derived).
set of RUNWAY: available = { r | r in RUNWAY where config.rate[r] != <> };

% Information on a flight that requires a slot in the TMI.
type flight = record(
                  TIME: preferred,    % preferred takeoff time
                  TIME: earliest,     % earliest possible takeoff time
                  TIME: latest,       % latest possible takeoff time
                  set of RUNWAY: rwy  % runways the flight is able to use
              );

% The flights participating in the TMI. Each flight is represented by a unique integer.
list of flight: flights;
set of int: FLIGHT = 1..length(flights);
 
/*
  Validate the input data.
*/

% The TMI period is non-empty.
constraint assert(config.start < config.end, "Start of TMI period (\(config.start)) must precede end (\(config.end))");

% A flight must be able to takeoff from one of the available runways.
constraint forall(f in FLIGHT)(assert(flights[f].rwy union available != {},  % should be intersect
                                      "Flight \(f) cannot use any of the available runways (\(available))"));

% The preferred takeoff time for a flight must be in its takeoff window.
constraint forall(f in FLIGHT)(assert(flights[f].earliest <= flights[f].preferred /\ flights[f].preferred <= flights[f].latest,
                                      "Flight \(f): preferred time (\(flights[f].preferred)) in not in " ++
                                      "takeoff window (\(flights[f].earliest)..\(flights[f].latest))"));

% The takeoff window for a flight must overlap the TMI period.
constraint forall(f in FLIGHT)(assert(flights[f].earliest <= config.end /\ config.start <= flights[f].latest,
                                      "Flight \(f): takeoff window (\(flights[f].earliest)..\(flights[f].latest)) " ++
                                      "does not fall within TMI period \(config.start)..\(config.end)"));

/*
  Decision variables: allocation of time and runway for flight.
*/

% The slot (target takeoff time) allocated to each flight. If <>, indicates flight was not allocated a slot.
array[FLIGHT] of var opt TIME: slot;

% The runway allocated to each flight. If <>, indicates flight was not allocated a slot.
array[FLIGHT] of var opt available: rwy;

% The flights that are allocated a slot by the TMI (derived).
var set of FLIGHT: allocated = { f | f in FLIGHT where slot[f] != <> };

% The flights that are excluded from the TMI (derived).
var set of FLIGHT: excluded = FLIGHT diff allocated;

/*
  Constraints
*/

% A flight must be allocated a runway it is able to use.
constraint forall(f in allocated)(rwy[f] in flights[f].rwy);

% The time allocated to a flight must fall within its takeoff window.
constraint forall(f in allocated)(flights[f].earliest <= slot[f] /\ slot[f] <= flights[f].latest);

% The time allocated to a flight must fall within the TMI period.
constraint forall(f in allocated)(config.start <= slot[f] /\ slot[f] <= config.end);

% Two flights allocated the same runway must depart at least the 'rate' duration apart.
constraint forall(f, g in allocated where f < g /\ rwy[f] = rwy[g])(abs(slot[f]-slot[g]) >= config.rate[rwy[f]]);

% 'slot' and 'rwy' are both undefined if flight not allocated a slot.
constraint forall(f in FLIGHT)(slot[f] = <> <-> rwy[f] = <>);

/*
  Objective
*/

% The length of time a flight's takeoff window overlaps the TMI period.
function var int: overlap(var FLIGHT: f) =
                  abs(max(config.start,flights[f].earliest) - min(config.end,flights[f].latest));

% The cost of a TMI is the sum of:
% - for each flight allocated a slot, the difference between its preferred time and allocated time;
% - for a flight not allocated a slot, the duration of its takeoff window.
var int: cost = sum(f in allocated)(abs(flights[f].preferred - slot[f])) +
               sum(f in excluded)(flights[f].latest - flights[f].earliest);
%                 sum(f in excluded)(overlap(f));

% The goal is to minimize the cost of the TMI.
solve minimize cost;