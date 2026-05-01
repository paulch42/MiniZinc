"""
Grammar actions that relate the grammar to the Python classes.

There is roughly one function per grammar rule that maps the output from the parser to the
corresponding Python object.
"""
from grammar import *
from model import *


def ident_action(tokens):
    return Ident(tokens[0])


def atomic_type_action(tokens):
    return AtomicType(Atomic(tokens[0]))


def set_type_action(tokens):
    return SetType(tokens[0])


def var_decl_action(tokens):
    return VarDecl(tokens[0], tokens[1])


def array_type_action(tokens):
    return ArrayType(tokens[0], tokens[1])


def var_type_action(tokens):
    return VarType(tokens[1]) if len(tokens) > 1 else tokens[0]


def bool_literal_action(tokens):
    return BoolLiteral(Bool(tokens[0]))


def int_literal_action(tokens):
    return IntLiteral(int(tokens[0], 0))


def float_literal_action(tokens):
    return FloatLiteral(float(tokens[0]))


def string_literal_action(tokens):
    return StringLiteral(tokens[0])


def set_literal_action(tokens):
    return SetLiteral(tokens)


def array_literal_action(tokens):
    return ArrayLiteral(tokens)


def call_expr_action(tokens):
    return CallExpr(tokens[0], tokens[1:])


def range_expr_action(tokens):
    if len(tokens) == 1:
        return tokens[0]
    return RangeExpr(tokens[0], tokens[1])


def include_item_action(tokens):
    return IncludeItem(tokens[0])


def annotation_action(tokens):
    return Annotation(list(tokens)) if list(tokens) else []


def var_decl_item_action(tokens):
    var = tokens[0]
    expr = tokens[-1] if len(tokens) > 1 and not isinstance(tokens[-1],
                                                            Annotation) else None
    ann = None
    if len(tokens) > (2 if expr else 1):
        ann = tokens[1]
    return VarDeclItem(var, ann, expr)


def constraint_item_action(tokens):
    return ConstraintItem(tokens[0], tokens[1] if len(tokens) > 1 else None)


def solve_item_action(tokens):
    ann = tokens[0] if isinstance(tokens[0], Annotation) else None
    i = 1 if ann else 0
    solve = Solve(tokens[i])
    i += 1
    expr = tokens[i] if i < len(tokens) else None
    return SolveItem(solve, ann, expr)


def predicate_item_action(tokens):
    return PredicateItem(tokens[0], tokens[1:])


def flatzinc_model_action(tokens):
    return FlatZincModel([t for t in tokens])


# Attach the actions to the grammar rules.
ident.set_parse_action(ident_action)
atomic_type.set_parse_action(atomic_type_action)
set_type.set_parse_action(set_type_action)
var_decl.set_parse_action(var_decl_action)
array_type.set_parse_action(array_type_action)
bool_literal.set_parse_action(bool_literal_action)
int_literal.set_parse_action(int_literal_action)
float_literal.set_parse_action(float_literal_action)
string_literal.set_parse_action(string_literal_action)
set_literal.set_parse_action(set_literal_action)
array_literal.set_parse_action(array_literal_action)
call_expr.set_parse_action(call_expr_action)
range_expr.set_parse_action(range_expr_action)
annotation.set_parse_action(annotation_action)
var_decl_item.set_parse_action(var_decl_item_action)
constraint_item.set_parse_action(constraint_item_action)
solve_item.set_parse_action(solve_item_action)
predicate_item.set_parse_action(predicate_item_action)
flatzinc_model.set_parse_action(flatzinc_model_action)
