import sys
from io import StringIO
from minizinc import Instance, Model, Solver
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF


def svg_cell(r: int, c: int, val: str, scale: int) -> str:
    step = scale // 2
    match val:
        case 'singleton':
            return f'<circle cx="{(c)*scale-step}" cy="{(r)*scale-step}\" r="{step}" fill="blue"/>'
        case 'left' | 'right' | 'top' | 'bottom' | 'interior':
            return f'<rect x="{(c-1)*scale}" y="{(r-1)*scale}" width="{scale}" height="{scale}" fill="blue" />'
        case _ : return ''


if len(sys.argv) < 2 or len(sys.argv) > 3:
    print('Usage: python3 battleships.py <data-file> [<output-file>]')
    sys.exit(0)
input_root = sys.argv[1]
input_file = sys.argv[1] + '.txt'
output_file = (sys.argv[2] if len(sys.argv) > 2 else input_root) + '.pdf'
lines = []
with open(input_file, 'r') as file:
    input_lines = file.readlines()
    for line in input_lines:
        l = line.strip()
        if l:
            lines.append(l)
ships_of_type = [int(s) for s in lines[0].split()]
num_in_row = [int(s) for s in lines[1].split()]
num_rows = len(num_in_row)
num_in_column = [int(s) for s in lines[2].split()]
num_cols = len(num_in_column)
grid = []
for l in lines[3:]:
    if len(l) != num_cols:
        print(f'Inconsistent numbers of cells in row "{l}"')
        exit(0)
    grid.append(list(l))
if len(grid) != num_rows:
    print(f'Inconsistent numbers of rows')
    exit(0)

model = Model('./battleships.mzn')
solver = Solver.lookup('huub')
instance = Instance(solver, model)
instance['num_rows'] = num_rows
instance['num_columns'] = num_cols
instance['num_ship_types'] = len(ships_of_type)
instance['ships_of_type'] = ships_of_type
instance['input_grid'] = grid
instance['num_in_row'] = num_in_row
instance['num_in_column'] = num_in_column
result = instance.solve()
if not result:
    print('No solution')
    sys.exit(0)
res = result['solution']

scale = 10
svg = [f'<svg width="{num_cols*scale}" height="{num_rows*scale}">']
svg.extend([svg_cell(r+1, c+1, res[r+1][c+1], scale) for r in range(num_rows) for c in range(num_cols)])
svg.extend('</svg>')
svgio = StringIO(''.join(svg))
drawing = svg2rlg(svgio)
if drawing:
    renderPDF.drawToFile(drawing, output_file)
