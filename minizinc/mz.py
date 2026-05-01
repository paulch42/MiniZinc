from actions import *
import sys

if len(sys.argv) < 2 or len(sys.argv) > 4:
    print('Usage: python3 mz.py <model-file>  [-block] [-inline]\n  - <model-file> does not include the ".mzn" extension')
    sys.exit(0)
file = f'{sys.argv[1]}.mzn'
ignore_block = True
ignore_inline = True
for a in sys.argv[2:]:
    match a:
        case '-block':
            ignore_block = False
        case '-inline':
            ignore_inline = False
        case _:
            print(f'Invalid argument: "{a}", ignoring')
try:
    model = mz_parse(ignore_inline,ignore_block).parse_file(file, parse_all=True)
    print(model[0])
except FileNotFoundError:
    print(f'File not found: "{file}"')
