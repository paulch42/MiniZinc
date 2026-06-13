include "globals.mzn";
include "ide/vis.mzn";
 
/*
  Parameters
*/

% extent into which the shapes are packed
int: x_extent;
set of int: X = 0..x_extent;
int: y_extent;
set of int: Y = 0..y_extent;
set of int: EXTENT = 0..max(x_extent,y_extent);

% the offsets and sizes of the rectangles
array[int,1..2] of int: rect_offset;
array[int,1..2] of int: rect_size;

% index set for rectangle offsets
set of int: ROFF = index_set_1of2(rect_offset);

% shapes represented as sets of (indexes of) rectangle offsets
list of set of ROFF: shape;
set of int: SHAPE = index_set(shape);

% sets of shape index sets, capturing all rotational variants of a shape
array[int] of set of int: shape_index; 
set of int: SHAPE_INDEX = index_set(shape_index);

/*
  Decision variables
*/

% x/y co-ordinate of the bottom left of each shape in the solution
array[SHAPE_INDEX,1..2] of var EXTENT: coord;

% selected rotational variant of a shape
array[SHAPE_INDEX] of var SHAPE: kind;

/*
  Constraints
*/

% constrain 'kind' to relevant shapes
constraint forall(i in SHAPE_INDEX)(kind[i] in shape_index[i]);

% pack the shapes
constraint geost_bb(rect_size, rect_offset, shape, coord, kind, [0,0], [x_extent, y_extent]);

% visualise the solution
output vis_geost_2d(rect_size, rect_offset, shape, coord, kind);