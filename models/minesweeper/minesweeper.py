import sys
from io import StringIO
from minizinc import Instance, Model, Solver
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF


def svg_cell(r: int, c: int, val: int, scale: int) -> str:
    step = scale // 2
    match val:
        case -1:
            return f'<circle cx="{(c+1)*scale-step}" cy="{(r+1)*scale-step}\" r="{step-1}" fill="blue"/>'
        case _:
            return f'<text x="{c*scale+(scale // 4)}" y="{(r+1)*scale-(scale // 4)}" >{val}</text>'


if len(sys.argv) < 2 or len(sys.argv) > 3:
    print('Usage: python3 minesweeper.py <data-file> [<output-file>]')
    sys.exit(0)
input_root = sys.argv[1]
input_file = sys.argv[1] + '.txt'
output_file = (sys.argv[2] if len(sys.argv) > 2 else input_file) + '.pdf'
lines = []
grid = []
with open(input_file, 'r') as file:
    lines = file.readlines()
    for line in lines:
        l = line.strip()
        if l:
            grid.append(l)
rows = len(grid)
cols = len(grid[0])
for row in grid:
    if len(row) != cols:
        print('Inconsistent numbers of cells in each row')
        exit(0)
mz_grid = [[None if cell == '.' else int(
    cell) for cell in row] for row in grid]
model = Model('./minesweeper.mzn')
solver = Solver.lookup('chuffed')
instance = Instance(solver, model)
instance['rows'] = rows
instance['columns'] = cols
instance['initial'] = mz_grid
result = instance.solve()
if not result:
    print('No solution')
    sys.exit(0)
res = result['solution']
scale = 20
svg = [f'<svg width="{cols*scale}" height="{rows*scale}">']
svg.extend([svg_cell(r, c, res[r][c], scale)
           for r in range(rows) for c in range(cols)])
svg.extend('</svg>')
svgio = StringIO(''.join(svg))
drawing = svg2rlg(svgio)
if drawing:
    renderPDF.drawToFile(drawing, output_file)
