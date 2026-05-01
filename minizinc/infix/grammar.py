from support import *

type_expr = pp.Forward()
expr = pp.Forward()
annotation = pp.Forward()
var_decl_item = pp.Forward()
constraint_item = pp.Forward()

operators:dict[str,tuple[pp.OpAssoc,int]] = {
    'default': (pp.opAssoc.LEFT,200),
    '++': (pp.opAssoc.RIGHT,300),
    '^': (pp.opAssoc.LEFT,400),
    '*': (pp.opAssoc.LEFT,500),
    '~*': (pp.opAssoc.LEFT,500),
    '/': (pp.opAssoc.LEFT,500),
    '~/': (pp.opAssoc.LEFT,500),
    'div': (pp.opAssoc.LEFT,500),
    '~div': (pp.opAssoc.LEFT,500),
    'mod': (pp.opAssoc.LEFT,500),
    '+': (pp.opAssoc.LEFT,600),
    '~+': (pp.opAssoc.LEFT,600),
    '-': (pp.opAssoc.LEFT,600),
    '~-': (pp.opAssoc.LEFT,600),
    'in': (pp.opAssoc.LEFT,1000),
    'subset': (pp.opAssoc.LEFT,1000),
    'superset': (pp.opAssoc.LEFT,1000),
    'union': (pp.opAssoc.LEFT,900),
    'diff': (pp.opAssoc.LEFT,900),
    'symdiff': (pp.opAssoc.LEFT,900),
    'intersect': (pp.opAssoc.LEFT,800),
    '..': (pp.opAssoc.LEFT,700),
    '<..': (pp.opAssoc.LEFT,700),
    '..<': (pp.opAssoc.LEFT,700),
    '<..<': (pp.opAssoc.LEFT,700),
    '<': (pp.opAssoc.LEFT,1200),
    '>': (pp.opAssoc.LEFT,1200),
    '<=': (pp.opAssoc.LEFT,1200),
    '>=': (pp.opAssoc.LEFT,1200),
    '==': (pp.opAssoc.LEFT,1100),
    '=': (pp.opAssoc.LEFT,1100),
    '~=': (pp.opAssoc.LEFT,1100),
    '!=': (pp.opAssoc.LEFT,1100),
    '~!=': (pp.opAssoc.LEFT,1100),
    '/\\': (pp.opAssoc.LEFT,1300),
    '\\/': (pp.opAssoc.LEFT,1400),
    'xor': (pp.opAssoc.LEFT,1400),
    '<-': (pp.opAssoc.LEFT,1500),
    '->': (pp.opAssoc.LEFT,1500),
    '<->': (pp.opAssoc.LEFT,1600),
}

keyword = kw(['include','any','enum','type','constraint','solve','satisfy','minimize','maximize','output','annotation',
              'predicate','test','function','var','par','opt','set','of','bool','int','float','string','ann','array','list',
              'tuple','record','true','false','if','then','else','elseif','endif','in','where'])

inline_comment = '%' + pp.rest_of_line

block_comment = pp.c_style_comment

comment = inline_comment | block_comment

quoted_ident = pp.Combine("'" + pp.Regex(r'[ a-zA-Z0-9_\-\.,;:=<>/?~!$@#%^&+*(){}\[\]\\]*') + "'")

ident = ~keyword + pp.Combine(opt(exact('_')) + pp.Word(pp.srange("[a-zA-Z]"), pp.srange("[a-zA-Z0-9_]"))) | quoted_ident

anon_var = skip('_')

# Productions related to type expressions

type_variable = pp.Combine(exact('$') + pp.Word(pp.srange("[a-zA-Z$]"), pp.srange("[a-zA-Z0-9_]")))

atomic_type = kw('bool int float string ann')

any_type = kwskip('any') + opt(type_variable)

set_type = kwskip('set') + kwskip('of') + type_expr

option_type = kwskip('opt') + type_expr

tuple_type = kwskip('tuple') + delimit('(',iterate(type_expr,',',True),')')

var_decl = type_expr + skip(':') + ident

record_type = kwskip('record') + delimit('(',iterate(var_decl,',',True),')')

array_type = (kwskip('array') + delimit('[',iterate(type_expr,',',True),']') | kwskip('list')) + kwskip('of') + type_expr

qualified_type = (kw('var') | skip('par')) + type_expr

basic_type = expr | ident | type_variable | atomic_type | any_type | set_type | option_type | tuple_type | record_type | array_type | qualified_type

type_expr <<= iterate(basic_type,'++')

# Productions related to value expressions

absent_literal = skip('<>')

bool_literal = kw('true false')

int_literal = pp.Regex('0x[0-9a-fA-F]+') | pp.Regex('0o[0-7]+') | pp.Regex('[0-9]+')

float_literal = pp.Regex(r'[0-9]+\.[0-9]+([eE][-+]?[0-9]+)?') | pp.Regex(r'[0-9]+(\.[0-9]+)?[eE][-+]?[0-9]+')

raw_string = pp.Regex(r'[ a-zA-Z0-9_\-\.,;:\'=<>/?~!$@#%^&+*(){}\[\]\\]*').leave_whitespace()

embedded_expr = delimit(r'\(',expr,')')

string_literal = delimit('"',raw_string,'"')

unary_op = exact('+ -') | kw('not')

unary_expr = unary_op + expr

num_bin_op = exact('+ - * / ^ ~+ ~- ~* ~/ ~div') | kw('div mod')

eq_bin_op = exact('<= >= < > == = != ~= ~!=')

bool_bin_op = exact('<-> <- -> \\/ /\\') | kw('xor')

set_bin_op = exact('<..< <.. ..< ..') | kw('in subset superset union diff symdiff intersect')

other_bin_op = exact('++') | kw('default')

# Note: constraints bool_bin_op < eq_bin_op, set_bin_op < eq_bin_op, other_bin_op < num_bin_op
bin_op = bool_bin_op | other_bin_op | eq_bin_op | num_bin_op | set_bin_op

quoted_op = pp.Combine(skip("'") + bin_op + skip("'"))

expr_seq = iterate(expr,',',True)

set_literal = delimit('{',opt(expr_seq),'}')

condition = kwskip('where') + expr

generator = iterate((ident | anon_var),',',True) + kwskip('in') + expr + opt(condition)

set_comp = delimit('{',(expr + skip('|') + iterate(generator,',',True)),'}')

array_literal = delimit('[',opt(expr_seq),']')

array_literal_2d = delimit('[|',opt(iterate(expr_seq,'|',False)),'|]')

array_comp = delimit('[',(expr + skip('|') + iterate(generator,',',True)),']')

index_tuple = expr | delimit('(',expr_seq,')')

indexed_expr = index_tuple + skip(':') + expr + opt(skip(',') + expr)

indexed_array_literal = delimit('[',opt(iterate(indexed_expr,',',True)),']')

indexed_array_literal_2d = skip('TODO')

indexed_array_comp = delimit('[',(indexed_expr + skip('|') + iterate(generator,',',True)),']')

tuple_literal = delimit('(',expr_seq,')')

labelled_expr = ident + skip(':') + expr

record_literal = delimit('(',iterate(labelled_expr,',',True),')')

conditional_expr = kwskip('if') + expr + kwskip('then') + expr + (kwskip('elseif') + expr + kwskip('then') + expr)[...] + opt(kwskip('else') + expr) + kwskip('endif')

let_expr = kwskip('let') + skip('{') + iterate((var_decl_item|constraint_item),';',True) + skip('}') + kwskip('in') + expr

# In MiniZinc grammar this is identical to call_expr. Not used here to avoid conflict.
ann_expr = ident + opt(delimit('(', expr_seq,')'))

# In MiniZinc grammar parenthesised expression sequence is optional. Mandatory here to avoid conflict with identifiers.
call_expr = (ident | quoted_op) + delimit('(', expr_seq,')')

call_comp_expr = (ident | quoted_op) + delimit('(',iterate(generator,',',True),')') + delimit('(',expr,')')

basic_expr = delimit('(',expr,')') | anon_var | absent_literal | bool_literal | float_literal | int_literal | string_literal | set_literal | set_comp | array_literal | indexed_array_literal | array_literal_2d | array_comp | tuple_literal | record_literal | conditional_expr | let_expr | unary_expr | call_comp_expr | call_expr | ident | quoted_op

array_accessor = delimit('[',expr_seq,']')

field_accessor = skip('.') + (ident | int_literal)

qualified_expr = basic_expr + (array_accessor | field_accessor)[...]

annotated_expr = qualified_expr + annotation

annotation <<= (skip('::') + qualified_expr)[...]

def op(id:str) -> tuple[str,int,pp.OpAssoc]:
    return (id,2,operators[id][0])

expr <<= pp.infix_notation(annotated_expr, [op('default'),op('++'),op('^'),op('*'),op('~*'),op('/'),op('~/'),op('div'),op('~div'),op('mod'),op('+'),op('~+'),op('-'),op('~-'),op('in'),op('subset'),op('superset'),op('union'),op('diff'),op('symdiff'),op('intersect'),op('..'),op('<..'),op('..<'),op('<..<'),op('<'),op('>'),op('<='),op('>='),op('=='),op('='),op('~='),op('!='),op('~!='),op('/\\'),op('\\/'),op('xor'),op('<-'),op('->'),op('<->')])

enum_list = delimit('{',iterate(ident,',',True),'}')

enum_anon = (anon_var | kw('anon_enum')) + delimit('(',expr,')')

enum_construct = ident + delimit('(',ident,')')

enum_cases = enum_list | enum_anon | enum_construct

include_item = kwskip('include') + string_literal

var_decl_item <<= var_decl + annotation + opt(skip('=') + expr)

enum_item = kwskip('enum') + ident + annotation + opt(skip('=') + iterate(enum_cases,'++'))

type_synonym_item = kwskip('type') + ident + annotation + skip('=') + type_expr

assign_item = ident + skip('=') + expr

string_annotation = skip('::') + string_literal

constraint_item <<= kwskip('constraint') + opt(string_annotation) + expr

solve_item = kwskip('solve') + annotation + (kw('satisfy') | kw('minimize') + expr | kw('maximize') + expr)

output_item = kwskip('output') + opt(string_annotation) + expr

function_defn = ident + opt(delimit('(',iterate(var_decl,',',True),')')) + annotation + opt(skip('=') + expr)

predicate_item = kwskip('predicate') + function_defn

test_item = kwskip('test') + function_defn

function_item = kwskip('function') + type_expr + skip(':') + function_defn

annotation_item = kwskip('annotation') + ident + opt(delimit('(',iterate(var_decl,',',True),')')) + opt(skip('=') + expr)

model_item = include_item | var_decl_item | enum_item | type_synonym_item | assign_item | constraint_item | solve_item | output_item | predicate_item | test_item | function_item | annotation_item

model = (block_comment | model_item + skip(';'))[...]

model.ignore(inline_comment)