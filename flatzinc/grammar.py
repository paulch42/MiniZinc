"""
FlatZinc pyparsing grammar.

Apart from a couple of minor deviations is compliant with the FlatZinc grammar defined in
https://docs.minizinc.dev/en/stable/fzn-spec.html#grammar.

The grammar is defined to allow the generation of a coherent Python object hierarchy.
Consequently, at least superficially, it looks significantly different from the official FlatZinc grammar.

The grammar is more liberal than the official grammar so models that would be trapped by the
FlatZinc parser are accepted in this parser.
"""
from support import *

ignore_inline_comment = True

basic_type = pp.Forward()
type_expr = pp.Forward()
range_expr = pp.Forward()

# Keywords: see section 4.1.3 of the MiniZinc Reference Manual.
keyword = kw('ann annotation any array bool case constraint diff div else elseif endif enum false float function '
             'if in include int intersect let list maximize minimize mod not of op opt output par predicate record '
             'satisfy set solve string subset superset symdiff test then true tuple type union var where xor')

ident = ~keyword + pp.Combine(opt(exact('_')) + pp.Word(
    pp.srange("[a-zA-Z]"), pp.srange("[a-zA-Z0-9_]")))

#
# Productions related to type expressions.
#

atomic_type = kw('bool int float')

set_type = kwskip('set') + kwskip('of') + basic_type

array_type = kwskip('array') + skip('[') + basic_type + skip(']') + kwskip('of') + type_expr

basic_type <<= range_expr | atomic_type | set_type | array_type

type_expr <<= opt(kw('var')) + basic_type

#
# Productions related to value expressions.
#

bool_literal = kw('true false')

int_literal = pp.Regex(
    '[-]?0x[0-9a-fA-F]+') | pp.Regex('[-]?0o[0-7]+') | pp.Regex('[-]?[0-9]+')

float_literal = pp.Regex(
    r'[-]?[0-9]+\.[0-9]+([eE][-+]?[0-9]+)?') | pp.Regex(r'[-]?[0-9]+[eE][-+]?[0-9]+')

raw_string = pp.Regex(
    r'[ a-zA-Z0-9_\-\.,;:\'=<>/\\?~!$@#%^&+*(){}\[\]]*').leave_whitespace()

# Doesn't support embedded " in the string, even if escaped by \.
string_literal = delimit('"', raw_string, '"')

expr_seq = iterate(range_expr, ',', True)

set_literal = delimit('{', opt(expr_seq), '}')

array_literal = delimit('[', opt(expr_seq), ']')

call_expr = ident + delimit('(', opt(expr_seq), ')')

basic_expr = bool_literal | float_literal | int_literal | string_literal | set_literal | array_literal | call_expr | ident

range_expr <<= basic_expr + opt(skip('..') + basic_expr)

#
# Productions related to top-level model items.
#

annotation = (skip('::') + basic_expr)[...]

var_decl = type_expr + skip(':') + ident

var_decl_item = var_decl + annotation + opt(skip('=') + range_expr)

constraint_item = kwskip('constraint') + call_expr + annotation

solve_item = kwskip('solve') + annotation + (kw('satisfy')
                                             | kw('minimize') + basic_expr | kw('maximize') + basic_expr)

predicate_item = kwskip('predicate') + ident + \
    delimit('(', opt(iterate(var_decl, ',', True)), ')')

predicates = (predicate_item + skip(';'))[...]

var_decls = (var_decl_item + skip(';'))[...]

constraints = (constraint_item + skip(';'))[...]

flatzinc_model = predicates + var_decls + constraints + solve_item + skip(';')

inline_comment = '%' + pp.rest_of_line

flatzinc_model.ignore(inline_comment)
