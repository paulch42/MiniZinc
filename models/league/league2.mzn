% Run with Huub for best performance.

include "globals.mzn";

/*
  Parameters
*/

% number of teams in the league
int: num_teams;
set of int: TEAM = 1..num_teams;

% pairs of teams that cannot play at home in the same round
array[int,1..2] of TEAM: co_home;

% total number of games to be played
int: total_games = num_teams * (num_teams-1);

% number of games each round
int: games_per_round = num_teams div 2;
set of int: GAME = 1..games_per_round;

% number of rounds
int: num_rounds = total_games div games_per_round;
set of int: ROUND = 1..num_rounds;

% the maximum consecutive home or away games
int: max_consecutive = 2;

% the minimum number of rounds before two teams can play each other again
int: min_gap = num_teams div 4;

/*
  Decision Variables
*/

% the season schedule
array[ROUND,GAME,1..2] of var TEAM: schedule;

% sequence of opponents for each team
array[TEAM,ROUND] of var TEAM: opponent;

% home/away indication for each team in each round; 1=home, 0=away, -1=not playing
array[TEAM,ROUND] of var -1..1: home_away;

/*
  Constraints
*/
               
% 1: channel 'opponent' and 'schedule'       
constraint forall(t in TEAM, r in ROUND where home_away[t,r] != -1)
                 (opponent[t,r] = let {var TEAM: op;
                                       var GAME: g;
                                       constraint schedule[r,g,1] = t \/ schedule[r,g,2] = t;
                                       constraint schedule[r,g,1] = op \/ schedule[r,g,2] = op;
                                       constraint t != op}
                                  in op);

% 2: channel 'home_away' and 'schedule'
constraint forall(r in ROUND, g in GAME)(home_away[schedule[r,g,1],r] = 1 /\ home_away[schedule[r,g,2],r] = 0);
constraint forall(t in TEAM, r in ROUND)(home_away[t,r] = -1 <-> not (t in array1d(schedule[r,GAME,1..2])));

% 3: symmetry breaking: order of games in a round
constraint forall(r in ROUND, g in 1..games_per_round-1)(schedule[r,g,1] < schedule[r,g+1,1]);

% 4: symmetry breaking: order of rounds
constraint value_precede_chain([i|i in TEAM],schedule[ROUND,1,1]);

% 5: no team involved in more than one game in a round
constraint forall(r in ROUND)(all_different([schedule[r,g,i] | g in GAME, i in 1..2]));

% 6: teams play each other exactly twice, once home and once away
constraint forall(t,u in TEAM where t < u)(sum(r in ROUND, g in GAME)(schedule[r,g,1..2] = [t,u]) = 1);
constraint forall(t,u in TEAM where t < u)(sum(r in ROUND, g in GAME)(schedule[r,g,1..2] = [u,t]) = 1);

% 7: at least 'min_gap' rounds elapse before playing the same team again
constraint forall(t in TEAM, i in 1..num_rounds-min_gap)(all_different(opponent[t,i..i+min_gap]));

% 8: a team plays no more than 'max_consecutive' home or away games in a row (including byes)
constraint forall(t in TEAM)
                 (sliding_among(0,max_consecutive,max_consecutive+1,row(home_away,t),{1,-1}));
constraint forall(t in TEAM)
                 (sliding_among(0,max_consecutive,max_consecutive+1,row(home_away,t),{0,-1}));

% 9: avoid coincident home games for teams so specified
constraint forall(i in index_set_1of2(co_home), r in ROUND)
                 (let {array[GAME] of var TEAM: home = schedule[r,GAME,1]}
                  in not (co_home[i,1] in home /\ co_home[i,2] in home));

% var int: cost;
% constraint cost = sum(t in TEAM, r in 1..num_rounds-1)(home_away[t,r] = home_away[t,r+1]);
% solve minimize cost;