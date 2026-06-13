/*
  Given is a rectilinear shape represented by an array of 0/1 values.
  
  Calculate a minimal set of rectangles that are non-overlapping and
  which combined exactly cover the shape.
*/
include "globals.mzn";

% extent in the X co-ordinate direction
int: x_extent;
set of int: X = 0..x_extent-1;
set of int: X_E = X union {x_extent};

% extent in the Y co-ordinate direction
int: y_extent;
set of int: Y = 0..y_extent-1;
set of int: Y_E = Y union {y_extent};

% the input rectilinear shape
array[1..y_extent,1..x_extent] of 0..1: input_shape;

% translate input from array row/column view to x/y co-ordinate view
array[X,Y] of 0..1: shape = array2d(X,Y,[ input_shape[y_extent-j+1,i]
                                        | i in 1..x_extent, j in 1..y_extent
                                        ]);

% estimate of the maximum number of rectangles in the shape
% the value has a significant impact on the solution time
int: max_rects = max(x_extent,y_extent);
set of int: RECT = 1..max_rects;

% decision variables: for each rectangle x position, y position, x size, y size
% an unused rectangle has 0 size and position set to x_extent/y_extent
array[RECT] of var X_E: x;
array[RECT] of var Y_E: y;
array[RECT] of var X_E: dx;
array[RECT] of var Y_E: dy;

% rectangles must fit within the extent of the original shape
constraint forall(r in RECT)(x[r]+dx[r] <= x_extent /\ y[r]+dy[r] <= y_extent);

% rectangles must overlap the original shape
constraint forall(r in RECT where dx[r] != 0,
                  i in x[r]..min(x_extent-1,x[r]+dx[r]-1),
                  j in y[r]..min(y_extent-1,y[r]+dy[r]-1))
                 (shape[i,j] = 1);

% all rectangles must be disjoint
constraint diffn_nonstrict(x,y,dx,dy);

% symmetry breaking: lexicographically order rectanges by x/y co-ordinate
constraint forall(r in 1..max_rects-1)(lex_lesseq([x[r],y[r]],[x[r+1],y[r+1]]));

% the size of an undefined rect is 0
% default x/y co-ordinates of undefined rects to appear at end of solution array
constraint forall(r in RECT)(dx[r] = 0 <-> dy[r] = 0);
constraint forall(r in RECT)(dx[r] = 0 <-> x[r] = x_extent);
constraint forall(r in RECT)(dx[r] = 0 <-> y[r] = y_extent);

% the cumulative size of the rectangles must equal the size of the original shape
constraint sum(shape) = sum(r in RECT)(dx[r]*dy[r]);

% the number of rectangles that constitute the rectilinear shape
var int: num_rect;
constraint num_rect = count(r in RECT)(dx[r] != 0);

% goal is to minimise the number of rectangles
solve :: seq_search([int_search(x,input_order,indomain_min),
                     int_search(y,input_order,indomain_min)])
         minimize num_rect;