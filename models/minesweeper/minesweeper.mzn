/*
  Parameters
*/

% Number of rows in the grid.
int: rows;
set of int: ROW = 1..rows;

% Number of colums in the grid.
int: columns;
set of int: COLUMN = 1..columns;

% Cell values: -1 = bomb, 0..8 = number of neighbouring cells with a bomb.
set of int: CELL = -1..8;
int: bomb = -1;

% Initial (fixed) configuration: number of neighbouring cells with a bomb (for some cells).
array[ROW,COLUMN] of opt CELL: initial;

constraint assert(forall(r in ROW, c in COLUMN)(initial[r,c] != bomb), "Bomb in initial configuration");

/*
  Decision Variables
*/

% Solution: each cell is either a bomb or a count of neighbouring cells with bombs.
array[ROW,COLUMN] of var CELL: solution;

/*
  Functions and predicates.
*/

% Count the number of neighbouring cells containing bombs.
function var int: neighbouring_bombs(ROW: r, COLUMN: c) =
    count(x in max(1,r-1)..min(rows,r+1), y in max(1,c-1)..min(columns,c+1))(solution[x,y] = bomb);

/*
  Constraints
*/

% Solution must retain values from initial configuration.
constraint forall(r in ROW, c in COLUMN)(occurs(initial[r,c]) -> solution[r,c] = initial[r,c]);

% Identify the cells with bombs that satisfy the initial configuration.
constraint forall(r in ROW, c in COLUMN)(solution[r,c] != bomb <-> solution[r,c] = neighbouring_bombs(r,c));

/*
  Output
*/

function string: output_row(array[int] of var CELL: row) =
    concat(i in index_set(row))(if fix(row[i]) = bomb then "*" else show(row[i]) endif);

output [output_row(solution[r,COLUMN]) ++ "\n" | r in ROW];