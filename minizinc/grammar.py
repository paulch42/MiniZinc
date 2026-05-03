"""
The MiniZinc pyparsing grammar.

Apart from a couple of minor deviations is compliant with the MiniZinc grammar defined in
https://docs.minizinc.dev/en/stable/spec.html#full-grammar.

The grammar is defined to allow the generation of a coherent Python object hierarchy.
Consequently, at least superficially, it looks somewhat different from the official MiniZinc grammar.

The grammar is more liberal than the official grammar so models that would be trapped by the
MiniZinc parser are accepted in this parser.
"""
from support import *

basic_type = pp.Forward()
type_expr = pp.Forward()
binary_expr = pp.Forward()
var_decl_item = pp.Forward()
constraint_item = pp.Forward()

# Keywords: see section 4.1.3 of the MiniZinc Reference Manual.
keyword = kw('ann annotation any array bool case constraint diff div else elseif endif enum false float function '
             'if in include int intersect let list maximize minimize mod not of op opt output par predicate record '
             'satisfy set solve string subset superset symdiff test then true tuple type union var where xor')

unary_op = exact('+ -') | kw('not')

binary_op = kw('div mod xor in subset superset union diff symdiff intersect default') | exact(
    '<-> <- -> \\/ /\\ ++ <= >= < > == = != ~= ~!= + - * / ^ ~+ ~- ~* ~/ ~div <..< <.. ..< ..')

quoted_ident = pp.Combine(
    "'" + ~(binary_op + exact("'")) + pp.Regex(r'[ a-zA-Z0-9_\-\.,;:=<>/?~!$@#%^&+*(){}\[\]|\\]+') + "'")

ident = ~keyword + pp.Combine(opt(exact('_')) + pp.Word(
    pp.srange("[a-zA-Z]"), pp.srange("[a-zA-Z0-9_]"))) | quoted_ident

anon_var = skip('_')

#
# Productions related to type expressions.
#

type_variable = pp.Combine(
    exact('$') + pp.Word(pp.srange("[a-zA-Z$]"), pp.srange("[a-zA-Z0-9_]")))

atomic_type = kw('bool int float string ann')

any_type = kwskip('any') + opt(type_variable)

set_type = kwskip('set') + kwskip('of') + basic_type

option_type = kwskip('opt') + basic_type

tuple_type = kwskip('tuple') + delimit('(', iterate(type_expr, ',', True), ')')

var_decl = type_expr + skip(':') + ident

record_type = kwskip('record') + \
    delimit('(', iterate(var_decl, ',', True), ')')

array_type = (kwskip('array') + delimit('[', iterate(
    type_expr, ',', True), ']') | kwskip('list')) + kwskip('of') + type_expr

basic_type <<= binary_expr | ident | type_variable | atomic_type | any_type | set_type | option_type | tuple_type | record_type | array_type

var_type = opt(kw('var') | skip('par')) + basic_type

type_expr <<= var_type + (exact('++') + var_type)[...]

#
# Productions related to value expressions.
#

absent_literal = skip('<>')

bool_literal = kw('true false')

int_literal = pp.Regex(
    '0x[0-9a-fA-F]+') | pp.Regex('0o[0-7]+') | pp.Regex('[0-9]+')

float_literal = pp.Regex(r'[0-9]+\.[0-9]+([eE][-+]?[0-9]+)?') | pp.Regex(r'[0-9]+[eE][-+]?[0-9]+') | pp.Regex(r'0[xX]([0-9a-fA-F]*\.[0-9a-fA-F]+|[0-9a-fA-F]+\.)[pP][-+]?[0-9]+') | pp.Regex('0[xX][0-9a-fA-F]+[pP][-+]?[0-9]+')

raw_string = pp.Regex(
    r'[ a-zA-Z0-9_\-\.,;:\'=<>/\\?~!$@#%^&+*(){}\[\]]*').leave_whitespace()

mixed_string = (pp.SkipTo(r'\(').leave_whitespace(
) + skip(r'\(') + binary_expr + skip(')'))[...] + pp.Regex(r'.*').leave_whitespace()

# Doesn't support embedded " in the string, even if escaped by \.
string_literal = delimit('"', raw_string, '"')

# This handles embedded " in the string, but it swallows the \ of the \( delimiter.
# string_literal = pp.QuotedString('"',esc_char='\\',convert_whitespace_escapes=False)

quoted_op = pp.Combine(skip("'") + binary_op + skip("'"))

expr_seq = iterate(binary_expr, ',', True)

set_literal = delimit('{', opt(expr_seq), '}')

condition = kwskip('where') + binary_expr

generator = iterate((ident | anon_var), ',', True) + \
    kwskip('in') + binary_expr + opt(condition)

set_comp = delimit(
    '{', (binary_expr + skip('|') + iterate(generator, ',', True)), '}')

array_literal = delimit('[', opt(expr_seq), ']')

array_literal_2d = delimit(
    '[|', opt(iterate(expr_seq, exact('|')+~exact(']'), True)), '|]')

array_comp = delimit(
    '[', (binary_expr + skip('|') + iterate(generator, ',', True)), ']')

tuple_index = binary_expr | delimit('(', expr_seq, ')')

indexed_expr = tuple_index + skip(':') + binary_expr + opt(skip(',') + binary_expr)

indexed_array_literal = delimit(
    '[', opt(iterate(indexed_expr, ',', True)), ']')

indexed_array_literal_2d = skip('TODO')

indexed_array_comp = delimit(
    '[', (indexed_expr + skip('|') + iterate(generator, ',', True)), ']')

tuple_literal = delimit('(', expr_seq, ')')

labelled_expr = ident + skip(':') + binary_expr

record_literal = delimit('(', iterate(labelled_expr, ',', True), ')')

conditional_expr = kwskip('if') + binary_expr + kwskip('then') + binary_expr + (kwskip('elseif') +
                                                                  binary_expr + kwskip('then') + binary_expr)[...] + opt(kwskip('else') + binary_expr) + kwskip('endif')

let_expr = kwskip('let') + skip('{') + iterate((var_decl_item |
                                                constraint_item), ';', True) + skip('}') + kwskip('in') + binary_expr

call_expr = (ident | quoted_op) + delimit('(', expr_seq, ')')

call_comp_expr = (ident | quoted_op) + delimit('(',
                                               iterate(generator, ',', True), ')') + delimit('(', binary_expr, ')')

basic_expr = delimit('(', binary_expr, ')') | absent_literal | bool_literal | float_literal | int_literal | string_literal | set_literal | set_comp | array_literal | indexed_array_literal | array_literal_2d | array_comp | tuple_literal | record_literal | conditional_expr | let_expr | call_comp_expr | call_expr | ident | anon_var | quoted_op

array_accessor = delimit('[', expr_seq, ']')

field_accessor = skip('.') + (ident | int_literal)

qualified_expr = basic_expr + (array_accessor | field_accessor)[...]

annotated_expr = qualified_expr + (exact('::') + qualified_expr)[...]

unary_expr = unary_op[...] + annotated_expr

# The following collection of productions reflect the precedence hierarchy of MiniZinc binary operators.
# There is one production for each precedence class.
# pyparsing has a very convenient feature for handling precedence and associativity of binary operators,
# see 'infix_notation', however performance suffers badly hence handled in the grammar explicitly.

default_expr = unary_expr + (kw('default') + unary_expr)[...]

join_expr = default_expr + (exact('++') + default_expr)[...]

pow_expr = join_expr + (exact('^') + join_expr)[...]

product_expr = pow_expr + \
    ((exact('* / ~* ~/') | kw('div mod ~div')) + pow_expr)[...]

sum_expr = product_expr + (exact('+ - ~+ ~-') + product_expr)[...]

range_expr = sum_expr + opt(exact('.. <.. ..< <..<') + sum_expr)

intersect_expr = range_expr + (kw('intersect') + range_expr)[...]

set_op_expr = intersect_expr + (kw('union diff symdiff') + intersect_expr)[...]

set_test_expr = set_op_expr + opt(kw('in subset superset') + set_op_expr)

eq_expr = set_test_expr + opt(exact('== = != ~= ~!=') + set_test_expr)

# Exclude '-' after'<' to allow '<-' (production 'iff_expr').
ineq_expr = eq_expr + opt((exact('<= >= >') | exact('<')+~ exact('-').leave_whitespace()) + eq_expr)

and_expr = ineq_expr + (exact('/\\') + ineq_expr)[...]

or_expr = and_expr + ((exact('\\/') | kw('xor')) + and_expr)[...]

iff_expr = or_expr + (exact('<- ->') + or_expr)[...]

binary_expr <<= iff_expr + (exact('<->') + iff_expr)[...]

# End of binary operator productions.

enum_list = delimit('{', iterate(ident, ',', True), '}')

enum_anon = (anon_var | kw('anon_enum')) + delimit('(', binary_expr, ')')

enum_construct = ident + delimit('(', ident, ')')

enum_cases = enum_list | enum_anon | enum_construct

#
# Productions related to top-level model items.
#

include_item = kwskip('include') + string_literal

annotation = (skip('::') + qualified_expr)[...]

var_decl_item <<= var_decl + annotation + opt(skip('=') + binary_expr)

enum_item = kwskip('enum') + ident + annotation + \
    opt(skip('=') + iterate(enum_cases, '++'))

type_synonym_item = kwskip('type') + ident + annotation + skip('=') + type_expr

assign_item = ident + skip('=') + binary_expr

string_annotation = skip('::') + string_literal

constraint_item <<= kwskip('constraint') + opt(string_annotation) + binary_expr

solve_item = kwskip('solve') + annotation + (kw('satisfy')
                                             | kw('minimize') + binary_expr | kw('maximize') + binary_expr)

output_item = kwskip('output') + opt(string_annotation) + binary_expr

function_defn = ident + \
    opt(delimit('(', iterate(var_decl, ',', True), ')')) + \
    annotation + opt(skip('=') + binary_expr)

predicate_item = kwskip('predicate') + function_defn

tst_item = kwskip('test') + function_defn

function_item = kwskip('function') + type_expr + skip(':') + function_defn

annotation_item = kwskip('annotation') + ident + opt(
    delimit('(', iterate(var_decl, ',', True), ')')) + opt(skip('=') + binary_expr)

# If in-line comments are ignored:
# - they can appear anywhere allowed by the MiniZinc specification;
# - '%' may not be the first non-whitespace character in a string literal.
# If in-line comments are not ignored:
# - they can only appear between top-level model items;
# - '%' may appear anywhere in a string literal.
inline_comment = '%' + pp.rest_of_line

# If block comments are ignored they can appear anywhere allowed by the MiniZinc specification.
# If not ignored, they can only appear between top-level model items, otherwise an error is thrown.
block_comment = pp.c_style_comment

comment_item = inline_comment | block_comment

model_item = include_item | var_decl_item | enum_item | type_synonym_item | assign_item | constraint_item | solve_item | output_item | predicate_item | tst_item | function_item | annotation_item | comment_item

minizinc_model = (comment_item | model_item + skip(';'))[...] + opt(model_item + comment_item[...])

def mz_parse(ignore_inline=True,ignore_block=True):
    if ignore_inline:
        minizinc_model.ignore(inline_comment)
    if ignore_block:
        minizinc_model.ignore(block_comment)
    return minizinc_model