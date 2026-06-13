import sys
import re
from minizinc import Instance, Model, Solver
from rectoff import *


def get_shape_strs(lines: list[str], index: int, shapes_strs: list[list[str]]) -> int:
    while index < len(lines) and not lines[index]:
        index += 1
    strs = []
    while index < len(lines) and lines[index]:
        strs.append(lines[index])
        index += 1
    if strs:
        width = len(strs[0])
        for s in strs[1:]:
            if len(s) != width:
                print(f'Inconsistent shape: {strs}')
                sys.exit(0)
        shapes_strs.append(strs)
        return index
    return -1


def rectify(strs: list[str]) -> Shape | None:
    xe = len(s[0])
    ye = len(s)
    grid = [[1 if i == '*' else 0 for i in s] for s in strs]
    model = Model('./rectilinear.mzn')
    solver = Solver.lookup('chuffed')
    instance = Instance(solver, model)
    instance['x_extent'] = xe
    instance['y_extent'] = ye
    instance['input_shape'] = grid
    result = instance.solve()
    if not result:
        print(f'No solution for {s}')
        return None
    shape = Shape(xe, ye)
    for i in range(result['num_rect']):
        shape.add(RectOff(result['x'][i], result['y']
                  [i], result['dx'][i], result['dy'][i]))
    return shape


if len(sys.argv) < 2 or len(sys.argv) > 3:
    print('Usage: python3 rectilinear.py [-u] <data-file>')
    sys.exit(0)
data_file = sys.argv[-1]
unary = False
if len(sys.argv) == 3:
    if sys.argv[1] != '-u':
        print(f'Unknown argument: "{sys.argv[1]}"')
        sys.exit(0)
    unary = True
shapes_strs = []
with open(data_file, 'r') as file:
    header = file.readline().strip()
    extent = re.split(r"\s+", header)
    if len(extent) != 2:
        print(f'Invalid header (2 numbers expected): "{header}"')
        sys.exit(0)
    x_extent = int(extent[0])
    y_extent = int(extent[1])
    lines = [l.strip() for l in file.readlines()]
    index = 0
    index = get_shape_strs(lines, index, shapes_strs)
    while index != -1:
        index = get_shape_strs(lines, index, shapes_strs)
if not shapes_strs:
    print(f'No shapes found in file: "{data_file}"')
    sys.exit(0)

shapes = []
for s in shapes_strs:
    shape = rectify(s)
    if shape:
        orientations = shape.orientations(unary)
        shapes.append(orientations)
rokeys = {}
roxy = []
rodxy = []
for so in shapes:
    for s in so.shapes:
        for ro in s.rects:
            h = hash(ro)
            if h not in rokeys:
                rokeys[h] = len(rokeys)
                roxy.append([ro.x,ro.y])
                rodxy.append([ro.dx,ro.dy])
ro_indices=[]
for so in shapes:
    for s in so.shapes:
        inds=set()
        for ro in s.rects:
            h = hash(ro)
            inds.add(rokeys[h]+1)
        ro_indices.append(inds)
count = 1
shape_indices = []
for so in shapes:
    i = len(so.shapes)
    shape_indices.append(set(range(count,count+i)))
    count += i
model = Model('./pack.mzn')
solver = Solver.lookup('chuffed')
instance = Instance(solver, model)
instance['x_extent'] = x_extent
instance['y_extent'] = y_extent
instance['rect_offset'] = roxy
instance['rect_size'] = rodxy
instance['shape'] = ro_indices
instance['shape_index'] = shape_indices
result = instance.solve()
if not result:
    print('No solution')
    sys.exit(0)
print('----')
print(f'x_extent={x_extent};')
print(f'y_extent={y_extent};')
print(f'rect_offset=[|{"|".join([",".join([str(i) for i in r]) for r in roxy])}|];')
print(f'rect_size=[|{"|".join([",".join([str(i) for i in r]) for r in rodxy])}|];')
print(f'shape={ro_indices};')
print(f'shape_index={shape_indices};')
print('----')
print(f'coord={result["coord"]};')
print(f'kind={result["kind"]};')