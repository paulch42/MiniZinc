from actions import *
import sys

if len(sys.argv) != 2:
    print('Usage: python3 fz.py <model-file>  (<model-file> does not include the ".fzn" extension)')
    sys.exit(0)
file = f'{sys.argv[1]}.fzn'
try:
    model = flatzinc_model.parse_file(file,parse_all=True)
    print(model[0])
except FileNotFoundError:
    print(f'File not found: "{file}"')