% Run with Chuffed solver for best performance
include "globals.mzn";

/*
  Parameters
*/

% the size of the puzzle
int: rows;
set of int: ROW = 1..rows;
int: cols;
set of int: COL = 1..cols;
set of int: RC = 1..max(rows,cols);
int: num_cells = rows*cols;

% track pieces; some are fixed
enum track_piece = {ns,ew,ne,nw,se,sw};
list of tuple(ROW,COL,track_piece): fixed;
int: num_fixed = length(fixed);

% number of track pieces in each row and column
array[ROW] of COL: row_counts;
array[COL] of ROW: col_counts;

% the start and end point cells
array[1..2] of RC: start = [fixed[1].1, fixed[1].2];
array[1..2] of RC: end = [fixed[num_fixed].1, fixed[num_fixed].2];

% the size of the solution path is the number of pieces to be placed
int: num_pieces = sum(row_counts);
set of int: PATH = 1..num_pieces;

/*
  Validate input
*/

constraint assert(sum(row_counts) = sum(col_counts), "Inconsistent row (\(sum(row_counts)) and column (\(sum(col_counts))) counts");
constraint assert(start[1] in {1,rows} \/ start[2] in {1,cols}, "Invalid start piece \(start)");
constraint assert(end[1] in {1,rows} \/ end[2] in {1,cols}, "Invalid end piece \(end)");

/*
  Decision variables
*/

% what track piece is placed in each cell; <> for an empty cell
array[ROW,COL] of var opt track_piece: solution;

% solution path; sequence of cells from 'start' to 'end'
array[PATH] of var ROW: pathr;           % row indices of path
array[PATH] of var COL: pathc;           % column indices of path
array[PATH] of var 1..num_cells: pathrc; % encoded co-ordinates of path; allows fast search with gecode

/*
  Constraints
*/

% is the supplied co-ordinate either the start point or end point
predicate end_point(ROW:i, COL:j) = ([i,j] = start \/ [i,j] = end);

% adjacent cells are connected by a valid piece
predicate connected(var ROW: thisr, var COL: thisc, var opt track_piece: piece, var ROW: nextr, var COL: nextc) =
  if     piece = ns then nextr in {thisr+1,thisr-1} /\ thisc = nextc
  elseif piece = ew then nextr=thisr /\ nextc in {thisc+1,thisc-1}
  elseif piece = se then (nextr = thisr /\ nextc = thisc+1) \/ (nextr = thisr+1 /\ nextc = thisc)
  elseif piece = nw then (nextr = thisr /\ nextc = thisc-1) \/ (nextr = thisr-1 /\ nextc = thisc)
  elseif piece = sw then (nextr = thisr /\ nextc = thisc-1) \/ (nextr = thisr+1 /\ nextc = thisc)
  elseif piece = ne then (nextr = thisr /\ nextc = thisc+1) \/ (nextr = thisr-1 /\ nextc = thisc)
  else true
  endif;

% channel 'pathr/c' and 'pathrc'
constraint forall(p in PATH)(pathrc[p] = (pathr[p]-1) * cols + pathc[p]);

% channel 'pathr/c' and 'solution'
constraint forall(p in PATH)(solution[pathr[p],pathc[p]] != <>);

% the fixed pieces in the initial configuration must be retained
constraint forall(p in fixed)(solution[p.1,p.2] = p.3);

% solution is a continuous path
constraint forall(p in 1..num_pieces-1)(connected(pathr[p], pathc[p], solution[pathr[p],pathc[p]], pathr[p+1], pathc[p+1]));

% ensure the path does not visit any cell more than once 
constraint alldifferent(pathrc);

% constrain number of track pieces in each row and column
constraint forall(r in ROW)(count(c in COL)(solution[r,c] != <>) = row_counts[r]);
constraint forall(c in COL)(count(r in ROW)(solution[r,c] != <>) = col_counts[c]);

% The following collection of constraints are functionally redundant, but improve performance
% significantly by allowing solver to avoid dead end paths.

% constraints on track pieces:
% - a piece must be a start/end piece if it leads off the grid
% - the ends of a piece must connect to another piece
constraint forall(r in ROW, c in COL where solution[r,c] = ns)((r in {1,rows} -> end_point(r,c)) /\
                                                         if r > 1 then solution[r-1,c] in {ns,sw,se} else true endif /\
                                                         if r < rows then solution[r+1,c] in {ns,nw,ne} else true endif);
                                                         
constraint forall(r in ROW, c in COL where solution[r,c] = ew)((c in {1,cols} -> end_point(r,c)) /\
                                                         if c > 1 then solution[r,c-1] in {ew,ne,se} else true endif /\
                                                         if c < cols then solution[r,c+1] in {ew,nw,sw} else true endif);

constraint forall(r in ROW, c in COL where solution[r,c] = se)((r = rows \/ c = cols -> end_point(r,c)) /\
                                                         if r < rows then solution[r+1,c] in {ns,nw,ne} else true endif /\
                                                         if c < cols then solution[r,c+1] in {ew,nw,sw} else true endif);

constraint forall(r in ROW, c in COL where solution[r,c] = nw)((1 in {r,c} -> end_point(r,c)) /\
                                                         if r > 1 then solution[r-1,c] in {ns,sw,se} else true endif /\
                                                         if c > 1 then solution[r,c-1] in {ew,ne,se} else true endif);

constraint forall(r in ROW, c in COL where solution[r,c] = sw)((r=rows \/ c=1 -> end_point(r,c)) /\
                                                         if r < rows then solution[r+1,c] in {ns,nw,ne} else true endif /\
                                                         if c > 1 then solution[r,c-1] in {ew,ne,se} else true endif);

constraint forall(r in ROW, c in COL where solution[r,c] = ne)((r=1 \/ c=cols -> end_point(r,c)) /\
                                                         if r > 1 then solution[r-1,c] in {ns,sw,se} else true endif /\
                                                         if c < cols then solution[r,c+1] in {ew,nw,sw} else true endif);

/*
  Find a path that satisfies the constraints
*/
solve :: int_search(pathrc,input_order,indomain_max) satisfy;

% The remainder concerns output of a solution (in SVG)
int: scale = 10;
output "<svg width=\"\((cols+1)*scale)\" height=\"\((rows+1)*scale)\">\n";
output ["<polyline style=\"fill:none;stroke:red\" points=\""] ++ [ "\(pathc[p]*scale),\(pathr[p]*scale) " | p in PATH] ++ ["\"/>"];
output "</svg>\n";