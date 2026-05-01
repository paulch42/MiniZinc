% Number of minutes in a day.
int:  maxtime = 24 * 60;

% A time is represented as the number of minutes since midnight.
set of int: TIME = 0..maxtime-1;

% Maximum duration: two hours is a realistic upper limit.
int: maxduration = 120;

% A duration is represented as a number of minutes.
set of int: DURATION = 0..maxduration;

% The runways at the airport.
enum runway;

% Configuration information required to run a TMI.
type TMI_config = record(
                      string: id,   % TMI identifier
                      TIME: start,  % TMI commences
                      TIME: end,    % TMI finishes
                      array[runway] of opt DURATION: rate
                                    % The rate of each runway - the minimum duration between consecutive takeoffs.
                                    % If <>, indicates the runway does not participate in the TMI.
                  );

% The TMI configuration.
TMI_config: config;

% The runways participating in the TMI (derived).
set of runway: participating = { r | r in runway where config.rate[r] != <> };

% Information on a flight that requires a slot in the TMI.
type flight = record(
                  string: id,         % flight identifier (callsign)
                  TIME: preferred,    % preferred takeoff time
                  TIME: earliest,     % earliest possible takeoff time
                  TIME: latest,       % latest possible takeoff time
                  set of runway: rwy  % runways the flight is able to use
              );

% The flights participating in the TMI.
list of flight: flights;
set of int: FLIGHT = 1..length(flights);
 
/*
  Decision variables: allocation of time and runway for flight.
*/

% The slot (target takeoff time) allocated to each flight. If <>, indicates flight was not allocated a slot.
array[FLIGHT] of var opt TIME: slot;

% The runway allocated to each flight.
array[FLIGHT] of var opt participating: rwy;

% The flights that are allocated a slot by the TMI (derived).
var set of FLIGHT: allocated = { f | f in FLIGHT where slot[f] != <> };

% The flights that are excluded from the TMI (derived).
var set of FLIGHT: excluded = FLIGHT diff allocated;

/*
  Validate the input data.
*/

% The TMI period is non-empty.
constraint assert(config.start < config.end, "Start of TMI period (\(config.start)) must precede end (\(config.end))");

% A flight must be able to takeoff from one of the participating runways.
constraint forall(f in FLIGHT)(assert(flights[f].rwy intersect participating != {},
                                      "Flight \(f) cannot use any of the participating runways (\(participating))"));

% The preferred takeoff time for a flight must be in its takeoff window.
constraint forall(f in FLIGHT)(assert(flights[f].earliest <= flights[f].preferred /\ flights[f].preferred <= flights[f].latest,
                                      "Flight \(f): preferred time (\(flights[f].preferred)) in not in " ++
                                      "takeoff window (\(flights[f].earliest)..\(flights[f].latest))"));

% The takeoff window for a flight must overlap the TMI period.
constraint forall(f in FLIGHT)(assert(flights[f].earliest <= config.end /\ config.start <= flights[f].latest,
                                      "Flight \(f): takeoff window (\(flights[f].earliest)..\(flights[f].latest)) " ++
                                      "does not fall within TMI period \(config.start)..\(config.end)"));

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

/*
  Objective
*/

% The cost of a TMI is the sum of:
% - for each flight allocated a slot, the difference between its preferred time and allocated time;
% - for a flight not allocated a slot, the duration of its takeoff window.
var int: cost = sum(f in allocated)(abs(flights[f].preferred - slot[f])) +
                sum(f in excluded)(flights[f].latest - flights[f].earliest);

% The goal is to minimize the cost of the TMI.
solve minimize cost;

function string: format_time(var opt TIME: t) = pad(-2, show(t div 60), "0") ++ ":" ++ pad(-2, show(t mod 60), "0");

function string: pad(int: w, string: s, string: p) = concat(if w < 0
                                                            then [ p | i in 1..abs(w)-string_length(s) ] ++ [s]
                                                            else [s] ++ [ p | i in 1..abs(w)-string_length(s) ]
                                                            endif);

output [ "Schedule for TMI " ++ config.id ++ ":\n"] ++
       [ "    " ++ format_justify_string(-7, flights[f].id) ++ ": " ++ format_time(slot[f]) ++ " - \(rwy[f])\n" | f in fix(allocated) ] ++
       [ "excluded: " ] ++ [ flights[e].id ++ " " | e in fix(excluded) ] ++ [ "\ncost: \(cost)"];
