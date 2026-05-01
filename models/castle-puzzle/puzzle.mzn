% Run with Chuffed solver for best performance
include "globals.mzn";
  
% number of blocks, with extension to model forbidden cell
int: n;
set of int: BLOCK = 1..n;
set of int: BLOCKX = 1..n+1;

% rectangle/offsets
int: m;
set of int: ROFF = 1..m;
array[ROFF,1..4] of int: d;

% rectangle/offsets extended with the forbidden cell
set of int: ROFFX = 1..m+1;
array[ROFFX,1..4] of int: dx = array2d(ROFFX,1..4,[d[i,j] | i in ROFF,j in 1..4]++[0,0,1,1]);

% all possible shapes (including all relevant rotational variants)
set of int: SHAPE = index_set(shape);
list of set of ROFF: shape;

% all possible shapes extended with the forbidden cell
set of int: SHAPEX = index_set(shapex);
array[_] of set of ROFFX: shapex = shape++[{m+1}];

% forbidden cell
array[1..2] of int: exclude;

% dimensions of the board
int: width;
int: height;

% indices of rotational variants (set of shapes) for each block
array[BLOCK] of set of int: shapeind; 

% shape indices extended with forbidden cell
array[BLOCKX] of set of int: shapeindx = shapeind++[{length(shape)+1}];

% (x,y) co-ordiante of (left,bottom) of each block (including forbidden block)
array[BLOCKX] of var 0..width: x;
array[BLOCKX] of var 0..height: y;

% extract the offsets and sizes in form suitable for geost_bb
array[ROFFX,1..2] of int: rsize = array2d(ROFFX, 1..2, [dx[i,j] | i in ROFFX, j in 3..4]);
array[ROFFX,1..2] of int: roff = array2d(ROFFX, 1..2, [dx[i,j] | i in ROFFX, j in 1..2]);

% channel 'x' and 'y' with 'coord'
array[BLOCKX,1..2] of var int: coord;
constraint forall(i in BLOCKX)(coord[i,1] = x[i] /\ coord[i,2] = y[i]);

% constrain the forbidden cell
constraint x[n+1] = exclude[1];
constraint y[n+1] = exclude[2];

% constrain 'kind' to relevant shapes
array[BLOCKX] of var int: kind;
constraint forall(i in BLOCKX)(kind[i] in shapeindx[i]);

% pack the blocks
constraint geost_bb(2, rsize, roff, shapex, coord, kind, [0,0], [width, height]);

% the remainder outputs the solution
array[BLOCKX] of string: colour = ["red", "green", "blue", "aqua", "black", "violet", "slategrey", "saddlebrown", "olivedrab", "lightyellow"];

function string: draw_block(int: num, var int: xo, var int: yo, var set of ROFFX: rect) = concat([draw_rect(num,xo,yo,ro) | ro in fix(rect)]);

function string: draw_rect(int: num, var int: xo, var int: yo, var  ROFFX: ro) =
    "<rect style=\"fill:" ++ colour[num] ++ "\" width=\"\(dx[ro,3])\" height=\"\(dx[ro,4])\" x=\"\(xo+dx[ro,1])\" y=\"\(yo+dx[ro,2])\"/>";

int: scale = 10;
output "<svg width=\"\(width*scale)\" height=\"\(height*scale)\"><g transform=\"scale(\(scale))\">\n";
output [draw_block(b,x[b],y[b],shapex[kind[b]]) ++ "\n" | b in BLOCKX];
output "</g></svg>";