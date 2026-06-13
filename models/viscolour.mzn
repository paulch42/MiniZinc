include "globals.mzn";
include "ide/vis.mzn";
 
% extent into which the shapes are packed
int: x_extent = 11;
set of int: X = 0..x_extent;
int: y_extent = 9;
set of int: Y = 0..y_extent;
set of int: EXTENT = 0..max(x_extent,y_extent);

% the offsets and sizes of the rectangles
array[int,1..2] of int: rect_offset =
  [|0,0|0,2|1,4|0,2|2,0|4,2|0,1|2,0|2,3|0,1|1,0|3,0|0,0|0,3|0,0|3,1|0,1|1,0|0,0|1,0|0,1|2,1
   |2,4|3,0|1,0|1,5|4,1|0,1|1,0|5,3|0,2|1,2|3,0|4,3|1,0|0,1|4,0|0,0|1,1|1,2|1,0|2,1|0,0|0,0|];
array[int,1..2] of int: rect_size =
  [|4,2|6,2|3,1|2,4|2,6|1,3|6,2|3,1|4,2|1,3|2,6|2,4|4,3|3,1|3,4|1,3|4,3|3,1|1,3|3,4|2,1|5,3
   |4,1|3,1|3,5|1,2|1,4|5,3|4,1|2,1|1,4|3,5|1,2|1,3|2,3|3,2|1,3|3,1|3,1|2,3|1,3|3,2|5,4|4,5|];

% index set for rectangle offsets
set of int: ROFF = index_set_1of2(rect_offset);

% shapes represented as sets of (indexes of) rectangle offsets
list of set of ROFF: shape =
  [{1, 2, 3}, {4, 5, 6}, {8, 9, 7}, {10, 11, 12}, {13, 14}, {16, 15}, {17, 18}, {19, 20}, {24, 21, 22, 23},
   {27, 25, 10, 26}, {3, 28, 29, 30}, {32, 33, 34, 31}, {3, 35, 14}, {16, 36, 37}, {40, 38, 39}, {41, 10, 42}, {43}, {44}];
set of int: SHAPE = index_set(shape);

% sets of shape index sets, capturing all rotational variants of a shape
array[int] of set of int: shape_index = [{1, 2, 3, 4}, {8, 5, 6, 7}, {9, 10, 11, 12}, {16, 13, 14, 15}, {17, 18}]; 
set of int: SHAPE_INDEX = index_set(shape_index);

% x/y co-ordinate of the bottom left of each shape in the solution
array[SHAPE_INDEX,1..2] of var EXTENT: coord;

% selected rotational variant of a shape
array[SHAPE_INDEX] of var SHAPE: kind;

% constrain 'kind' to relevant shapes
constraint forall(i in SHAPE_INDEX)(kind[i] in shape_index[i]);

% pack the shapes
constraint geost_bb(rect_size, rect_offset, shape, coord, kind, [0,0], [x_extent, y_extent]);

% visualise the solution
output vis_geost_2d(rect_size, rect_offset, shape, coord, kind);