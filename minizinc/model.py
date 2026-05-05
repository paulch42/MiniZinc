"""
Python class hierarchy that represents a MiniZinc model.

The structure of the class hierarchy closely follows the structuire of the grammar.

Simple data classes with a __str__ method. Given a valid MiniZinc model, the __str__ output can be fed
back into MiniZinc and it remains valid, but it is not pretty printed.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import IntEnum, StrEnum, auto
from abc import ABC


def add_option(term, prefix=None):
    """
    Convenience function to format a term if defined, with optional prefix.

    Args:
        term: the term to be formatted
        prefix (optional): prefix text

    Returns:
        str: the formatted term, or empty string if not defined
    """
    return f'{prefix if prefix else ""}{term}' if term else ''


def delimit(term, test):
    """
    Convenience function to optionally delimit a term.

    Args:
        term: the term to be delimited
        test: True if term to be delimited

    Returns:
        str: the formatted term
    """
    return f'({term})' if test else str(term)


def fmt_list(lst, sep=',', at_start=False):
    """
    Format a list of terms inserting a separator between terms.

    Args:
        lst: list of terms
        sep (optional): separator

    Returns:
        str: the formatted list
    """
    return (sep if at_start else '') + sep.join([str(t) for t in lst])


class Assoc(IntEnum):
    LEFT = auto()
    RIGHT = auto()
    NONE = auto()


@dataclass
class AnonVar:

    def __str__(self):
        return '_'


@dataclass
class AbstractType(ABC):
    def precedence(self):
        return -1  # smaller than any binary type operator


@dataclass
class TypeVariable(AbstractType):
    id: str

    def __str__(self):
        return self.id


class Atomic(StrEnum):
    BOOL = auto()
    INT = auto()
    FLOAT = auto()
    STRING = auto()
    ANN = auto()


@dataclass
class AtomicType(AbstractType):
    typ: Atomic

    def __str__(self):
        return self.typ


@dataclass
class AnyType(AbstractType):
    id: TypeVariable | None = None

    def __str__(self):
        return 'any' + add_option(self.id, prefix=' ')


@dataclass
class SetType(AbstractType):
    typ: AbstractType

    def __str__(self):
        return f'set of {self.typ}'


@dataclass
class OptionType(AbstractType):
    typ: AbstractType

    def __str__(self):
        return f'opt {self.typ}'


@dataclass
class TupleType(AbstractType):
    typs: list[AbstractType] = field(default_factory=list)

    def __str__(self):
        return f'tuple({fmt_list(self.typs)})'


@dataclass
class VarDecl:
    typ: AbstractType
    id: Ident

    def __str__(self):
        return f'{self.typ}: {self.id}'


@dataclass
class RecordType(AbstractType):
    vdecls: list[VarDecl] = field(default_factory=list)

    def __str__(self):
        return f'record({fmt_list(self.vdecls)})'


@dataclass
class ArrayType(AbstractType):
    titem: AbstractType
    domains: list[AbstractType] = field(default_factory=list)

    def __str__(self):
        return (f'array[{fmt_list(self.domains)}]' if self.domains else 'list') + f' of {self.titem}'


@dataclass
class VarType(AbstractType):
    typ: AbstractType

    def __str__(self):
        return f'var {self.typ}'


class BinaryTypeOp(StrEnum):
    JOIN = "++"


type_operators: dict[BinaryTypeOp, tuple[Assoc, int]] = {
    BinaryTypeOp.JOIN: (Assoc.RIGHT, 300)}


@dataclass
class TypeExpr(AbstractType):
    left: AbstractType
    op: BinaryTypeOp
    right: AbstractType

    def __str__(self):
        """
        Format a binary type expression as a string.
        Inserts minimum parentheses to respect associativity and precedence.

        Returns:
            str: the formatted type expression
        """
        if (self.left.precedence() == self.precedence()):
            test = type_operators[self.op][0] == Assoc.RIGHT
        else:
            test = self.left.precedence() > self.precedence()
        left = delimit(self.left, test)
        if (self.right.precedence() == self.precedence()):
            test = type_operators[self.op][0] == Assoc.LEFT
        else:
            test = self.right.precedence() > self.precedence()
        right = delimit(self.right, test)
        return f'{left} {self.op} {right}'

    def precedence(self):
        return type_operators[self.op][1]


@dataclass
class AbstractExpr(ABC):
    def precedence(self):
        return -1  # smaller than any unary or binary operator


@dataclass
class Ident(AbstractExpr):
    id: str

    def __str__(self):
        return self.id


@dataclass
class AbsentLiteral(AbstractExpr):

    def __str__(self):
        return '<>'


class Bool(StrEnum):
    TRUE = auto()
    FALSE = auto()


@dataclass
class BoolLiteral(AbstractExpr):
    val: Bool

    def __str__(self):
        return str(self.val)


@dataclass
class IntLiteral(AbstractExpr):
    val: int

    def __str__(self):
        return str(self.val)


@dataclass
class FloatLiteral(AbstractExpr):
    val: float

    def __str__(self):
        return str(self.val)


@dataclass
class StringLiteral(AbstractExpr):
    strs: list[str] = field(default_factory=list)
    exprs: list[AbstractExpr] = field(default_factory=list)

    def __str__(self):
        return '"' + ''.join([f'{s}\\({e})' for (s, e) in zip(self.strs, self.exprs)]) + self.strs[-1] + '"'


class UnaryOp(StrEnum):
    NOT = "not"
    NOT_SYM = "¬"
    PLUS = "+"
    MINUS = "-"


unary_operators: dict[UnaryOp, tuple[Assoc, int]] = {
    # Precedence must be greater than anootation (::), but less than any other binary operator.
    UnaryOp.NOT: (Assoc.RIGHT, 50),
    UnaryOp.NOT_SYM: (Assoc.RIGHT, 50),
    UnaryOp.PLUS: (Assoc.RIGHT, 50),
    UnaryOp.MINUS: (Assoc.RIGHT, 50),
}


@dataclass
class UnaryExpr(AbstractExpr):
    expr: AbstractExpr
    op: UnaryOp

    def __str__(self):
        """
        Format a unary expression as a string.
        Inserts minimum parentneses to respect associativity and precedence.

        Returns:
            str: the formatted expression
        """
        test = self.expr.precedence() > self.precedence()
        return f'{self.op} {delimit(self.expr, test)}'

    def precedence(self):
        return unary_operators[self.op][1]


class BinaryOp(StrEnum):
    ANNOTATION = "::"
    DEFAULT = "default"
    JOIN = "++"
    POW = "^"
    TIMES = "*"
    TIMES_OPT = "~*"
    DIVIDE = "/"
    DIVIDE_OPT = "~/"
    DIV = "div"
    DIV_OPT = "~div"
    MOD = "mod"
    PLUS = "+"
    PLUS_OPT = "~+"
    MINUS = "-"
    MINUS_OPT = "~-"
    RANGE = ".."
    RANGE_EX_L = "<.."
    RANGE_EX_H = "..<"
    RANGE_EX_LH = "<..<"
    INTERSECT = "intersect"
    INTERSECT_SYM = "∩"
    UNION = "union"
    UNION_SYM = "∪"
    DIFF = "diff"
    SYMDIFF = "symdiff"
    IN = "in"
    IN_SYM = "∈"
    SUBSET = "subset"
    SUBSET_SYM = "⊆"
    SUPERSET = "superset"
    SUPERSET_SYM = "⊇"
    EQEQ = "=="
    EQ = "="
    EQ_OPT = "~="
    NEQ = "!="
    NEQ_SYM = "≠"
    NEQ_OPT = "~!="
    LT = "<"
    GT = ">"
    LEQ = "<="
    LEQ_SYM = "≤"
    GEQ = ">="
    GEQ_SYM = "≥"
    AND = "/\\"
    AND_SYM = "∧"
    OR = "\\/"
    OR_SYM = "∨"
    XOR = "xor"
    IF = "<-"
    IF_SYM = "←"
    ONLY_IF = "->"
    ONLY_IF_SYM = "→"
    IFF = "<->"


# Associativity and precedence table for the binary opertors, as defined in the MiniZinc Reference Manual.
operators: dict[BinaryOp, tuple[Assoc, int]] = {
    BinaryOp.ANNOTATION: (Assoc.LEFT, 0),
    BinaryOp.DEFAULT: (Assoc.LEFT, 200),
    BinaryOp.JOIN: (Assoc.RIGHT, 300),
    BinaryOp.POW: (Assoc.LEFT, 400),
    BinaryOp.TIMES: (Assoc.LEFT, 500),
    BinaryOp.TIMES_OPT: (Assoc.LEFT, 500),
    BinaryOp.DIVIDE: (Assoc.LEFT, 500),
    BinaryOp.DIVIDE_OPT: (Assoc.LEFT, 500),
    BinaryOp.DIV: (Assoc.LEFT, 500),
    BinaryOp.DIV_OPT: (Assoc.LEFT, 500),
    BinaryOp.MOD: (Assoc.LEFT, 500),
    BinaryOp.PLUS: (Assoc.LEFT, 600),
    BinaryOp.PLUS_OPT: (Assoc.LEFT, 600),
    BinaryOp.MINUS: (Assoc.LEFT, 600),
    BinaryOp.MINUS_OPT: (Assoc.LEFT, 600),
    BinaryOp.RANGE: (Assoc.NONE, 700),
    BinaryOp.RANGE_EX_L: (Assoc.NONE, 700),
    BinaryOp.RANGE_EX_H: (Assoc.NONE, 700),
    BinaryOp.RANGE_EX_LH: (Assoc.NONE, 700),
    BinaryOp.INTERSECT: (Assoc.LEFT, 800),
    BinaryOp.INTERSECT_SYM: (Assoc.LEFT, 800),
    BinaryOp.UNION: (Assoc.LEFT, 900),
    BinaryOp.UNION_SYM: (Assoc.LEFT, 900),
    BinaryOp.DIFF: (Assoc.LEFT, 900),
    BinaryOp.SYMDIFF: (Assoc.LEFT, 900),
    BinaryOp.IN: (Assoc.NONE, 1000),
    BinaryOp.IN_SYM: (Assoc.NONE, 1000),
    BinaryOp.SUBSET: (Assoc.NONE, 1000),
    BinaryOp.SUBSET_SYM: (Assoc.NONE, 1000),
    BinaryOp.SUPERSET: (Assoc.NONE, 1000),
    BinaryOp.SUPERSET_SYM: (Assoc.NONE, 1000),
    BinaryOp.EQEQ: (Assoc.NONE, 1100),
    BinaryOp.EQ: (Assoc.NONE, 1100),
    BinaryOp.EQ_OPT: (Assoc.NONE, 1100),
    BinaryOp.NEQ: (Assoc.NONE, 1100),
    BinaryOp.NEQ_SYM: (Assoc.NONE, 1100),
    BinaryOp.NEQ_OPT: (Assoc.NONE, 1100),
    BinaryOp.LT: (Assoc.NONE, 1200),
    BinaryOp.GT: (Assoc.NONE, 1200),
    BinaryOp.LEQ: (Assoc.NONE, 1200),
    BinaryOp.LEQ_SYM: (Assoc.NONE, 1200),
    BinaryOp.GEQ: (Assoc.NONE, 1200),
    BinaryOp.GEQ_SYM: (Assoc.NONE, 1200),
    BinaryOp.AND: (Assoc.LEFT, 1300),
    BinaryOp.AND_SYM: (Assoc.LEFT, 1300),
    BinaryOp.OR: (Assoc.LEFT, 1400),
    BinaryOp.OR_SYM: (Assoc.LEFT, 1400),
    BinaryOp.XOR: (Assoc.LEFT, 1400),
    BinaryOp.IF: (Assoc.LEFT, 1500),
    BinaryOp.IF_SYM: (Assoc.LEFT, 1500),
    BinaryOp.ONLY_IF: (Assoc.LEFT, 1500),
    BinaryOp.ONLY_IF_SYM: (Assoc.LEFT, 1500),
    BinaryOp.IFF: (Assoc.LEFT, 1600),
}


@dataclass
class QuotedOp():
    op: BinaryOp

    def __str__(self):
        return f"'{self.op}'"


@dataclass
class ExprSeq():
    exprs: list[AbstractExpr] = field(default_factory=list)

    def __str__(self):
        return fmt_list(self.exprs)


@dataclass
class SetLiteral(AbstractExpr):
    members: list[AbstractExpr] = field(default_factory=list)

    def __str__(self):
        return f'{{{fmt_list(self.members)}}}'


@dataclass
class Condition():
    expr: AbstractExpr

    def __str__(self):
        return str(self.expr)


@dataclass
class Generator():
    domain: AbstractExpr
    ids: list[Ident | AnonVar] = field(default_factory=list)
    condition: AbstractExpr | None = None

    def __str__(self):
        return f'{fmt_list(self.ids, ",")} in {self.domain}{add_option(self.condition, prefix=" where ")}'


@dataclass
class SetComp(AbstractExpr):
    val: AbstractExpr
    qualifiers: list[Generator] = field(default_factory=list)

    def __str__(self):
        return f'{{{self.val} | {fmt_list(self.qualifiers)}}}'


@dataclass
class ArrayLiteral(AbstractExpr):
    members: list[AbstractExpr] = field(default_factory=list)

    def __str__(self):
        return f'[{fmt_list(self.members)}]'


@dataclass
class ArrayLiteral2D(AbstractExpr):
    members: list[list[AbstractExpr]] = field(default_factory=list)

    def __str__(self):
        return f'[| {" | ".join([fmt_list(es) for es in self.members])} |]'


@dataclass
class ArrayComp(AbstractExpr):
    val: AbstractExpr
    qualifiers: list[Generator] = field(default_factory=list)

    def __str__(self):
        return f'[{self.val} | {fmt_list(self.qualifiers)}]'


@dataclass
class IndexedExpr():
    index: AbstractExpr
    vals: list[AbstractExpr] = field(default_factory=list)

    def __str__(self):
        return f'{self.index}: {fmt_list(self.vals)}'


@dataclass
class IndexedArrayLiteral(AbstractExpr):
    members: list[IndexedExpr] = field(default_factory=list)

    def __str__(self):
        return f'[{fmt_list(self.members)}]'


@dataclass
class IndexedRow():
    index: AbstractExpr | None = None
    row: list[AbstractExpr] = field(default_factory=list)

    def __str__(self):
        prefix = f'{self.index}: ' if self.index else ''
        return prefix + fmt_list(self.row)


@dataclass
class IndexedArrayLiteral2D():
    column_indices: list[AbstractExpr] = field(default_factory=list)
    rows: list[IndexedRow] = field(default_factory=list)

    def __str__(self):
        cind = fmt_list(self.column_indices, ':')
        if cind:
            cind += ':'
            items = [cind] + self.rows
        else:
            items = self.rows
        return f'[| {" | ".join([str(i) for i in items])} |]'


@dataclass
class TupleLiteral(AbstractExpr):
    members: list[AbstractExpr] = field(default_factory=list)

    def __str__(self):
        return f'({fmt_list(self.members)})'


@dataclass
class LabelledExpr:
    label: Ident
    expr: AbstractExpr

    def __str__(self):
        return f'{self.label}: {self.expr}'


@dataclass
class RecordLiteral(AbstractExpr):
    members: list[LabelledExpr] = field(default_factory=list)

    def __str__(self):
        return f'({fmt_list(self.members)})'


@dataclass
class ConditionalExpr(AbstractExpr):
    test: list[AbstractExpr] = field(default_factory=list)
    action: list[AbstractExpr] = field(default_factory=list)
    otherwise: AbstractExpr | None = None

    def __str__(self):
        res = ''
        for index, (t, a) in enumerate(zip(self.test, self.action)):
            res += ('if' if index == 0 else ' elseif') + f' {t} then {a}'
        return res + add_option(self.otherwise, prefix=' else ') + ' endif'


@dataclass
class LetExpr(AbstractExpr):
    body: AbstractExpr
    local: list[VarDeclItem | ConstraintItem] = field(default_factory=list)

    def __str__(self):
        return f'let {{{fmt_list(self.local, ";")}}} in {self.body}'


@dataclass
class CallExpr(AbstractExpr):
    id: Ident | QuotedOp
    args: list[AbstractExpr] = field(default_factory=list)

    def __str__(self):
        return f'{self.id}({fmt_list(self.args)})'


@dataclass
class CallCompExpr(AbstractExpr):
    id: Ident | QuotedOp
    expr: AbstractExpr
    gens: list[Generator] = field(default_factory=list)

    def __str__(self):
        return f'{self.id}({fmt_list(self.gens)})({str(self.expr)})'


@dataclass
class ArrayAccessor():
    arg: list[AbstractExpr] = field(default_factory=list)

    def __str__(self):
        return f'[{fmt_list(self.arg)}]'


@dataclass
class FieldAccessor():
    arg: Ident | IntLiteral

    def __str__(self):
        return f'.{self.arg}'


@dataclass
class QualifiedExpr(AbstractExpr):
    expr: AbstractExpr
    qualifier: list[ArrayAccessor | FieldAccessor] = field(
        default_factory=list)

    def __str__(self):
        return f'{self.expr}' + fmt_list(self.qualifier, "")

    def prune(self):
        return self if self.qualifier else self.expr


@dataclass
class AnnotatedExpr(AbstractExpr):
    expr: QualifiedExpr
    ann: Annotation | None = None

    def __str__(self):
        return f'{self.expr}{add_option(self.ann, prefix=" ")}'

    def prune(self):
        return self if self.ann else self.expr


@dataclass
class Annotation():
    ann: list[QualifiedExpr] = field(default_factory=list)

    def __str__(self):
        return fmt_list(self.ann, sep=' :: ', at_start=True)


@dataclass
class BinaryExpr(AbstractExpr):
    left: AbstractExpr
    op: BinaryOp
    right: AbstractExpr

    def __str__(self):
        """
        Format a binary expression as a string.
        Inserts minimum parentneses to respect associativity and precedence.

        Returns:
            str: the formatted expression
        """
        if (self.left.precedence() == self.precedence()):
            test = operators[self.op][0] == Assoc.RIGHT
        else:
            test = self.left.precedence() > self.precedence()
        left = delimit(self.left, test)
        if (self.right.precedence() == self.precedence()):
            test = operators[self.op][0] == Assoc.LEFT
        else:
            test = self.right.precedence() > self.precedence()
        right = delimit(self.right, test)
        return f'{left} {self.op} {right}'

    def precedence(self):
        return operators[self.op][1]


@dataclass
class Enum:
    pass


@dataclass
class EnumList(Enum):
    items: list[Ident] = field(default_factory=list)

    def __str__(self):
        return f'{{{fmt_list(self.items)}}}'


@dataclass
class EnumAnon(Enum):
    kind: AnonVar | None
    arg: AbstractExpr

    def __str__(self):
        return f'{"_" if self.kind else "anon_enum"}({self.arg})'


@dataclass
class EnumConstruct(Enum):
    wrapper: Ident
    base: Ident

    def __str__(self):
        return f'{self.wrapper}({self.base})'


@dataclass
class Item(ABC):
    pass


@dataclass
class IncludeItem(Item):
    file: str

    def __str__(self):
        return f'include {self.file}'


@dataclass
class VarDeclItem(Item):
    vdecl: VarDecl
    ann: Annotation | None = None
    expr: AbstractExpr | None = None

    def __str__(self):
        return f'{self.vdecl}{add_option(self.ann)}{add_option(self.expr, prefix=" = ")}'


@dataclass
class EnumItem(Item):
    id: Ident
    ann: Annotation | None = None
    enum: list[Enum] = field(default_factory=list)

    def __str__(self):
        res = f'enum {self.id}{add_option(self.ann)}'
        if self.enum:
            res += ' = ' + fmt_list(self.enum)
        return res


@dataclass
class TypeSynonymItem(Item):
    id: Ident
    type: TypeExpr
    ann: Annotation | None = None

    def __str__(self):
        return f'type {self.id}{add_option(self.ann)} = {self.type}'


@dataclass
class AssignItem(Item):
    id: Ident
    expr: AbstractExpr

    def __str__(self):
        return f'{self.id} = {self.expr}'


@dataclass
class ConstraintItem(Item):
    expr: AbstractExpr
    label: str | None = None

    def __str__(self):
        return f'constraint{add_option(self.label, prefix=" :: ")} {self.expr}'


class Solve(StrEnum):
    SATISFY = auto()
    MINIMIZE = auto()
    MAXIMIZE = auto()


@dataclass
class SolveItem(Item):
    stype: Solve
    ann: Annotation | None = None
    expr: AbstractExpr | None = None

    def __str__(self):
        res = f'solve{add_option(self.ann)} {self.stype}'
        match self.stype:
            case Solve.MINIMIZE | Solve.MAXIMIZE:
                res += f' {self.expr}'
        return res


@dataclass
class OutputItem(Item):
    expr: AbstractExpr
    label: str | None = None

    def __str__(self):
        return f'output{add_option(self.label, prefix=" :: ")} {self.expr}'


@dataclass
class FunctionDefn():
    id: Ident
    args: list[VarDecl] = field(default_factory=list)
    ann: Annotation | None = None
    body: AbstractExpr | None = None

    def __str__(self):
        res = f'{self.id}'
        if self.args:
            res += f'({fmt_list(self.args)})'
        return f'{res}{add_option(self.ann)}{add_option(self.body, prefix=" = ")}'


@dataclass
class PredicateItem(Item):
    func: FunctionDefn

    def __str__(self):
        return f'predicate {self.func}'


@dataclass
class TstItem(Item):
    func: FunctionDefn

    def __str__(self):
        return f'test {self.func}'


@dataclass
class FunctionItem(Item):
    type: TypeExpr
    func: FunctionDefn

    def __str__(self):
        return f'function {self.type}: {self.func}'


@dataclass
class AnnotationItem(Item):
    id: Ident
    decls: list[VarDecl] = field(default_factory=list)
    expr: AbstractExpr | None = None

    def __str__(self):
        res = f'annotation {self.id}'
        if self.decls:
            res += f'({fmt_list(self.decls)})'
        return f'{res}{add_option(self.expr, prefix=" = ")}'


@dataclass
class CommentItem(Item):
    comment: str

    def __str__(self):
        return self.comment


@dataclass
class MiniZincModel:
    items: list[Item] = field(default_factory=list)

    def __str__(self):
        return '\n'.join([str(i) + ("" if isinstance(i, CommentItem) else ";") for i in self.items])
