"""
Grammar actions that relate the grammar to the Python classes.

There is roughly one function per grammar rule that maps the output from the parser to the
corresponding Python object.
"""
from grammar import *
from model import *


def prune(tokens):
    if not isinstance(tokens, pp.ParseResults):
        return tokens
    return [prune(e) for e in list(tokens)]


def ident_action(tokens):
    return Ident(tokens[0])


def anon_var_action(_):
    return AnonVar()


def type_variable_action(tokens):
    return TypeVariable(tokens[0])


def atomic_type_action(tokens):
    return AtomicType(Atomic(tokens[0]))


def any_type_action(tokens):
    return AnyType(tokens[0] if tokens else None)


def set_type_action(tokens):
    return SetType(tokens[0])


def option_type_action(tokens):
    return OptionType(tokens[0])


def tuple_type_action(tokens):
    return TupleType(list(tokens))


def var_decl_action(tokens):
    return VarDecl(tokens[0], tokens[1])


def record_type_action(tokens):
    return RecordType(list(tokens))


def array_type_action(tokens):
    return ArrayType(tokens[-1],tokens[:-1])


def var_type_action(tokens):
    return VarType(tokens[1]) if len(tokens) > 1 else tokens[0]


def construct_type(arg):
    """
    Construct an expression from a list of expressions interleaved with binary operators.

    Args:
        arg: the operands of the iterated binary expression

    Returns:
        Expr: the constructed expression
    """
    if len(arg) == 1:
        return arg[0]
    operands = arg[::2]
    ops = arg[1::2]
    assoc = type_operators[BinaryTypeOp(ops[0])][0]
    if assoc == Assoc.LEFT:
        res = operands[0]
        rest = operands[1:]
        for (a, o) in zip(rest, ops):
            res = TypeExpr(res, BinaryTypeOp(o), a)
    else:
        res = operands[-1]
        rest = reversed(operands[:-1])
        ops = reversed(ops)
        for (a, o) in zip(rest, ops):
            res = TypeExpr(a, BinaryTypeOp(o), res)
    return res


def type_expr_action(tokens):
    return construct_type(list(tokens))


def absent_literal_action(_):
    return AbsentLiteral()


def bool_literal_action(tokens):
    return BoolLiteral(Bool(tokens[0]))


def int_literal_action(tokens):
    return IntLiteral(int(tokens[0], 0))


def float_literal_action(tokens):
    try:
        return FloatLiteral(float(tokens[0]))
    except:
        return FloatLiteral(float.fromhex(tokens[0]))


def string_literal_action(tokens):
    ms = mixed_string.parse_string(tokens[0])
    return StringLiteral([s.replace('"','\\"') for s in ms[0::2]], [e for e in ms[1::2]])


def quoted_op_action(tokens):
    return QuotedOp(BinaryOp(tokens[0]))


def expr_seq_action(tokens):
    return ExprSeq(list(tokens))


def set_literal_action(tokens):
    return SetLiteral(tokens[0].exprs if tokens else [])


def condition_action(tokens):
    return Condition(tokens[0])


def generator_action(tokens):
    condition = None
    last = len(tokens)-1
    if isinstance(tokens[last], Condition):
        condition = tokens[-1].expr
        last -= 1
    return Generator(tokens[last], tokens[:last], condition)


def set_comp_action(tokens):
    return SetComp(tokens[0], tokens[1:])


def array_literal_action(tokens):
    return ArrayLiteral(tokens[0].exprs if tokens else [])


def array_literal_2d_action(tokens):
    return ArrayLiteral2D([row.exprs for row in tokens])


def array_comp_action(tokens):
    return ArrayComp(tokens[0], tokens[1:])


def tuple_literal_action(tokens):
    return TupleLiteral(tokens[0].exprs)


def labelled_expr_action(tokens):
    return LabelledExpr(tokens[0], tokens[1])


def record_literal_action(tokens):
    return RecordLiteral(list(tokens))


def conditional_expr_action(tokens):
    return ConditionalExpr(tokens[0:-1:2], tokens[1::2], None if len(tokens) % 2 == 0 else tokens[-1])


def let_expr_action(tokens):
    return LetExpr(tokens[-1], tokens[:-1])


def call_expr_action(tokens):
    return CallExpr(tokens[0], tokens[1].exprs)


def call_comp_expr_action(tokens):
    return CallCompExpr(tokens[0], tokens[-1], tokens[1:-1])


def array_accessor_action(tokens):
    return ArrayAccessor(tokens[0].exprs)


def field_accessor_action(tokens):
    return FieldAccessor(tokens[0])


def qualified_expr_action(tokens):
    return QualifiedExpr(tokens[0], tokens[1:]).prune()


def unary_expr_action(tokens):
    expr = tokens[-1]
    for o in reversed(tokens[:-1]):
        expr = UnaryExpr(expr, UnaryOp(o))
    return expr

def construct(arg):
    """
    Construct a binary expression from a list of expressions interleaved with binary operators,
    taking account of associativity.

    Args:
        arg: the operands of the iterated binary expression

    Returns:
        Expr: the constructed expression
    """
    if not isinstance(arg, list):
        return arg
    if len(arg) == 1:
        return arg[0]
    operands = arg[::2]
    ops = arg[1::2]
    assoc = operators[ops[0]][0]
    if assoc == Assoc.LEFT:
        res = operands[0]
        rest = operands[1:]
        for (a, o) in zip(rest, ops):
            res = BinaryExpr(res, BinaryOp(o), a)
    else:
        res = operands[-1]
        rest = reversed(operands[:-1])
        ops = reversed(ops)
        for (a, o) in zip(rest, ops):
            res = BinaryExpr(a, BinaryOp(o), res)
    return res

def binary_op_action(tokens):
    return construct(prune(tokens))


def annotated_expr_action(tokens):
    return binary_op_action(tokens)


def default_expr_action(tokens):
    return binary_op_action(tokens)


def join_expr_action(tokens):
    return binary_op_action(tokens)


def pow_expr_action(tokens):
    return binary_op_action(tokens)


def product_expr_action(tokens):
    return binary_op_action(tokens)


def sum_expr_action(tokens):
    return binary_op_action(tokens)


def range_expr_action(tokens):
    return binary_op_action(tokens)


def intersect_expr_action(tokens):
    return binary_op_action(tokens)


def set_op_expr_action(tokens):
    return binary_op_action(tokens)


def set_test_expr_action(tokens):
    return binary_op_action(tokens)


def eq_expr_action(tokens):
    return binary_op_action(tokens)


def ineq_expr_action(tokens):
    return binary_op_action(tokens)


def and_expr_action(tokens):
    return binary_op_action(tokens)


def or_expr_action(tokens):
    return binary_op_action(tokens)


def iff_expr_action(tokens):
    return binary_op_action(tokens)


def binary_expr_action(tokens):
    return binary_op_action(tokens)


def enum_list_action(tokens):
    return EnumList(list(tokens))


def enum_anon_action(tokens):
    label = tokens[0] if isinstance(tokens[0], AnonVar) else None
    return EnumAnon(label, tokens[1])


def enum_construct_action(tokens):
    return EnumConstruct(tokens[0], tokens[1])


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


def enum_item_action(tokens):
    id = tokens[0]
    ann = tokens[1] if len(tokens) > 1 and isinstance(
        tokens[1], Annotation) else None
    i = 2 if ann else 1
    enum = [e for e in tokens[i:] if isinstance(e, Enum)]
    return EnumItem(id, ann, enum)


def type_synonym_item_action(tokens):
    id = tokens[0]
    ann = tokens[1] if len(tokens) > 1 and isinstance(
        tokens[1], Annotation) else None
    i = 2 if ann else 1
    return TypeSynonymItem(id, tokens[i], ann)


def assign_item_action(tokens):
    return AssignItem(tokens[0], tokens[1])


def constraint_item_action(tokens):
    return ConstraintItem(tokens[-1], tokens[0] if len(tokens) > 1 else None)


def solve_item_action(tokens):
    ann = tokens[0] if isinstance(tokens[0], Annotation) else None
    i = 1 if ann else 0
    solve = Solve(tokens[i])
    i += 1
    expr = tokens[i] if i < len(tokens) else None
    return SolveItem(solve, ann, expr)


def output_item_action(tokens):
    return OutputItem(tokens[-1], tokens[0] if len(tokens) > 1 else None)


def function_defn_action(tokens):
    id = tokens[0]
    args = [a for a in tokens[1:] if isinstance(a, VarDecl)]
    next = len(args)+1
    anns = None
    if len(tokens) > next and isinstance(tokens[next],Annotation):
        anns = tokens[next]
        next += 1
    body = tokens[-1] if len(tokens) > next else None
    return FunctionDefn(id, args, anns, body)


def predicate_item_action(tokens):
    return PredicateItem(tokens[0])


def tst_item_action(tokens):
    return TstItem(tokens[0])


def function_item_action(tokens):
    return FunctionItem(tokens[0], tokens[1])


def annotation_item_action(tokens):
    id = tokens[0]
    expr = tokens[-1] if isinstance(tokens[-1], BinaryExpr) else None
    args = tokens[1:-1] if expr else tokens[1:]
    return AnnotationItem(id, args, expr)


def block_comment_action(tokens):
    return CommentItem(tokens[0])


def inline_comment_action(tokens):
    return CommentItem(f'% {tokens[1]}')


def minizinc_model_action(tokens):
    return MiniZincModel([t for t in tokens])


# Attach the actions to the grammar rules.
ident.set_parse_action(ident_action)
anon_var.set_parse_action(anon_var_action)
type_variable.set_parse_action(type_variable_action)
atomic_type.set_parse_action(atomic_type_action)
any_type.set_parse_action(any_type_action)
set_type.set_parse_action(set_type_action)
option_type.set_parse_action(option_type_action)
tuple_type.set_parse_action(tuple_type_action)
var_decl.set_parse_action(var_decl_action)
record_type.set_parse_action(record_type_action)
array_type.set_parse_action(array_type_action)
var_type.set_parse_action(var_type_action)
type_expr.set_parse_action(type_expr_action)
absent_literal.set_parse_action(absent_literal_action)
bool_literal.set_parse_action(bool_literal_action)
int_literal.set_parse_action(int_literal_action)
float_literal.set_parse_action(float_literal_action)
string_literal.set_parse_action(string_literal_action)
expr_seq.set_parse_action(expr_seq_action)
quoted_op.set_parse_action(quoted_op_action)
set_literal.set_parse_action(set_literal_action)
condition.set_parse_action(condition_action)
generator.set_parse_action(generator_action)
set_comp.set_parse_action(set_comp_action)
array_literal.set_parse_action(array_literal_action)
array_literal_2d.set_parse_action(array_literal_2d_action)
array_comp.set_parse_action(array_comp_action)
tuple_literal.set_parse_action(tuple_literal_action)
labelled_expr.set_parse_action(labelled_expr_action)
record_literal.set_parse_action(record_literal_action)
conditional_expr.set_parse_action(conditional_expr_action)
let_expr.set_parse_action(let_expr_action)
call_expr.set_parse_action(call_expr_action)
call_comp_expr.set_parse_action(call_comp_expr_action)
array_accessor.set_parse_action(array_accessor_action)
field_accessor.set_parse_action(field_accessor_action)
qualified_expr.set_parse_action(qualified_expr_action)
unary_expr.set_parse_action(unary_expr_action)
annotated_expr.set_parse_action(annotated_expr_action)
default_expr.set_parse_action(default_expr_action)
join_expr.set_parse_action(join_expr_action)
pow_expr.set_parse_action(pow_expr_action)
product_expr.set_parse_action(product_expr_action)
sum_expr.set_parse_action(sum_expr_action)
range_expr.set_parse_action(range_expr_action)
intersect_expr.set_parse_action(intersect_expr_action)
set_op_expr.set_parse_action(set_op_expr_action)
set_test_expr.set_parse_action(set_test_expr_action)
eq_expr.set_parse_action(eq_expr_action)
ineq_expr.set_parse_action(ineq_expr_action)
and_expr.set_parse_action(and_expr_action)
or_expr.set_parse_action(or_expr_action)
iff_expr.set_parse_action(iff_expr_action)
binary_expr.set_parse_action(binary_expr_action)
enum_list.set_parse_action(enum_list_action)
enum_anon.set_parse_action(enum_anon_action)
enum_construct.set_parse_action(enum_construct_action)
include_item.set_parse_action(include_item_action)
annotation.set_parse_action(annotation_action)
var_decl_item.set_parse_action(var_decl_item_action)
enum_item.set_parse_action(enum_item_action)
type_synonym_item.set_parse_action(type_synonym_item_action)
assign_item.set_parse_action(assign_item_action)
constraint_item.set_parse_action(constraint_item_action)
solve_item.set_parse_action(solve_item_action)
output_item.set_parse_action(output_item_action)
function_defn.set_parse_action(function_defn_action)
predicate_item.set_parse_action(predicate_item_action)
tst_item.set_parse_action(tst_item_action)
function_item.set_parse_action(function_item_action)
annotation_item.set_parse_action(annotation_item_action)
block_comment.set_parse_action(block_comment_action)
inline_comment.set_parse_action(inline_comment_action)
minizinc_model.set_parse_action(minizinc_model_action)
