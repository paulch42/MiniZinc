# League Table

Given the number of teams (possibly odd) competing in a league, determine a schedule of games satisfying the following constraints:

- the competition is completed in a minimum number of rounds;
- teams play each other twice, once at home and once away;
- a team can play in at most one game each round;
- a minimum number of rounds must occur between the games when two teams play each other (calculated as "number of teams / 4");
- a team can have no more than two consecutive home or away games;
- some pairs of teams cannot both play at home in the same round.

If the number of teams is odd, then one team has a bye (doesn't play) in each round.

Two models are presented. In both, the key decision variable is 'schedule' that determines for each round and each game in a round, the home and away teams for that game. Additionally, 'home_away' determines for each team and each round, whether the team plays at home or away in that round.

Where the models differ is that [league1](league1.mzn) has the additional decision variable 'round' that for any two teams 'a' and 'b', in what round does 'a' (home) play 'b' (away), while [league2](league2.mzn) has the additional decision variable 'decision' that determines for any team and round, the opponent of that team.

Run with the command:
```
python3 league.py <m> <n>
```
where `<m>` is the model number (i.e. _league1.mzn_ or _league2.mzn_), and `<n>` is the data file number (1 through 5).