include "globals.mzn";

/*
  Parameters
*/

% Number of rows in the grid.
int: num_rows;
set of int: ROW = 1..num_rows;
set of int: ROW0 = 0..num_rows;

% Number of columns in the grid.
int: num_columns;
set of int: COLUMN = 1..num_columns;
set of int: COLUMN0 = 0..num_columns;

% The maximum extent of a row or column.
int: maxrc = max(num_rows,num_columns);
set of int: MAXRC = 1..maxrc;

% Number of different types of ships; the type is represented by the length of the ship.
int: num_ship_types;
set of int: SHIP_TYPE = 1..num_ship_types;

% The number of instances of each ship type.
array[SHIP_TYPE] of int: ships_of_type;

% The total number of ships.
int: num_ships = sum(ships_of_type);
set of int: SHIP = 1..num_ships;

% The type of each ship.
array[SHIP] of SHIP_TYPE: type_of = [t | t in SHIP_TYPE, _ in 1..ships_of_type[t]];

% Cells can contain a ship piece or be empty.
enum Cell = {singleton,left,right,top,bottom,interior,empty};

% ASCII representation of a cell; used to output solution.
array[Cell] of string: cell_to_str = ["o","<",">","^","v","#"," "];

% The input configuration.
array[ROW,COLUMN] of string: input_grid;

% The initial configuration for the MiniZinc model: derived from 'input_grid'.
array[ROW,COLUMN] of opt Cell: initial = array2d(ROW,COLUMN,[str_to_cell(input_grid[r,c]) | r in ROW, c in COLUMN]);

% The number of ship pieces in each row and column.
array[ROW] of int: num_in_row;
array[COLUMN] of int: num_in_column;

/*
  Decision Variables
*/

% The lexicographically (by row/column) smallest co-ordinate of the cells occupied by a ship.
array[SHIP] of var MAXRC: row_pos;
array[SHIP] of var MAXRC: col_pos;

% Orientation of a ship: 0=vertical, 1=horizontal.
array[SHIP] of var 0..1: orientation;

% The value assigned to each cell in the solution, including dummy row 0 and column 0.
array[ROW0,COLUMN0] of var Cell: solution;

/*
  Functions and predicates.
*/

% The width of a ship in the grid: 1 if vertical, otherwise the length of the ship.
function var MAXRC: width(SHIP: s) = if orientation[s] = 0 then 1 else type_of[s] endif;

% The height of a ship in the grid: 1 if horizontal, otherwise the length of the ship.
function var MAXRC: height(SHIP: s) = if orientation[s] = 0 then type_of[s] else 1 endif;

% Constraints on a ship oriented vertically.
predicate vertical(var ROW: r, var COLUMN: c, var MAXRC: size) =
  solution[r,c] = top /\ solution[r+size-1,c] = bottom /\ forall(i in r+1..min(r+size-2,num_rows))(solution[i,c] = interior);

% Constraints on a ship oriented horizontally.
predicate horizontal(var ROW: r, var COLUMN: c, var MAXRC: size) =
  solution[r,c] = left /\ solution[r,c+size-1] = right /\ forall(i in c+1..min(c+size-2,num_columns))(solution[r,i] = interior);

% Cell corresponding to an ASCII character; used to decode input.
function opt Cell: str_to_cell(string: s) =
         if s = "o" then singleton elseif s = "<" then left elseif s = ">" then right
         elseif s = "^" then top elseif s = "v" then bottom elseif s = "#" then interior
         elseif s = "x" then empty else <> endif;

/*
  Constraints
*/

% Channel 'row_pos'/'col_pos' with 'solution'.
constraint forall(s in SHIP)(if type_of[s] = 1
                             then solution[row_pos[s],col_pos[s]] = singleton
                             elseif orientation[s] = 0
                             then vertical(row_pos[s],col_pos[s],type_of[s])
                             else horizontal(row_pos[s],col_pos[s],type_of[s])
                             endif);

% Dummy row and column cells are always empty.
constraint forall(r in ROW)(solution[r,0] = empty);
constraint forall(c in COLUMN)(solution[0,c] = empty);

% Values in initial configuration must be respected.
constraint forall(r in ROW, c in COLUMN)(occurs(initial[r,c]) -> solution[r,c] = initial[r,c]);

% Ships are not adjacent to each other.
% Note: to enforce the constraint there must be a gap between ships, the ships are represented
% as rectangles in which the left and top border are included in the area occupied by the ship.
constraint diffn([row_pos[s]-1|s in SHIP],
                 [col_pos[s]-1|s in SHIP],
                 [height(s)+1|s in SHIP],
                 [width(s)+1|s in SHIP]);

% Correct number of ship pieces in each row and column.
constraint forall(r in ROW)(count(c in COLUMN)(solution[r,c] != empty) = num_in_row[r]);
constraint forall(c in COLUMN)(count(r in ROW)(solution[r,c] != empty) = num_in_column[c]);

/*
  Output
*/

function string: output_row(array[int] of var Cell: row) =
    concat(i in index_set(row))(cell_to_str[fix(row[i])]);

output [output_row(solution[r,COLUMN]) ++ "\n" | r in ROW];