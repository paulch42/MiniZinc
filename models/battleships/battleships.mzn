% Run with Chuffed or Huub solver for best performance.

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

% The different kinds of ship pieces that can be assigned to a cell.
enum ShipPiece = {singleton,left,right,top,bottom,interior};

% The orientation of a ship on the grid.
enum Orientation = {vertical,horizontal};

% Cells can be ship pieces or empty.
enum Cell = P(ShipPiece) ++ {empty};

% The initial configuration.
array[ROW,COLUMN] of opt Cell: initial;

% The number of ship pieces in each row and column.
array[ROW] of int: num_in_row;
array[COLUMN] of int: num_in_column;

/*
  Decision Variables
*/

% The lexicographically (by row/column) smallest co-ordinate of the cells occupied by a ship.
array[SHIP] of var MAXRC: row_pos;
array[SHIP] of var MAXRC: col_pos;

% Orientation of a ship.
array[SHIP] of var Orientation: orientation;

% The value assigned to each cell in the solution, including dummy row 0 and column 0.
array[ROW0,COLUMN0] of var Cell: solution;

/*
  Functions and predicates.
*/

% The width of a ship in the grid: 1 if vertical, otherwise the length of the ship.
function var MAXRC: width(SHIP: s) = if orientation[s] = vertical then 1 else type_of[s] endif;

% The height of a ship in the grid: 1 if horizontal, otherwise the length of the ship.
function var MAXRC: height(SHIP: s) = if orientation[s] = vertical then type_of[s] else 1 endif;

% Constraints on a ship oriented vertically.
predicate vertical(var ROW: r, var COLUMN: c, var MAXRC: size) =
  solution[r,c] = P(top) /\ solution[r+size-1,c] = P(bottom) /\ forall(i in r+1..min(r+size-2,num_rows))(solution[i,c] = P(interior));

% Constraints on a ship oriented horizontally.
predicate horizontal(var ROW: r, var COLUMN: c, var MAXRC: size) =
  solution[r,c] = P(left) /\ solution[r,c+size-1] = P(right) /\ forall(i in c+1..min(c+size-2,num_columns))(solution[r,i] = P(interior));

/*
  Constraints
*/

% Channel 'row_pos'/'col_pos' with 'solution'.
constraint forall(s in SHIP)(if type_of[s] = 1
                             then solution[row_pos[s],col_pos[s]] = P(singleton)
                             elseif orientation[s] = vertical
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
  Output (SVG)
*/

function string: draw_cell(ROW: r, COLUMN: c) =
  if fix(solution[r,c]) = P(singleton)
  then "<circle cx=\"\(c*scale-step)\" cy=\"\(r*scale-step)\" r=\"\(step)\" fill=\"blue\" />\n"
  elseif fix(solution[r,c]) != empty
  then "<rect x=\((c-1)*scale) y=\((r-1)*scale) width=\(scale) height=\(scale) fill=\"blue\" />\n"
  else ""
  endif;
  
int: scale = 10;
int: step = scale div 2;
output "<svg width=\"\(num_columns*scale)\" height=\"\(num_rows*scale)\">\n";
output [draw_cell(r,c) | r in ROW, c in COLUMN];
output "</svg>";