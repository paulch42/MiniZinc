"""
Python class hierarchy that represents a FlatZinc model.

The structure of the class hierarchy closely follows the structuire of the grammar.

Simple data classes with a __str__ method. Given a valid FlatZinc model, the __str__ output can be fed
back into MiniZinc and it remains valid, but it is not pretty printed.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import StrEnum, auto
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


@dataclass
class AbstractType(ABC):
    pass


class Atomic(StrEnum):
    BOOL = auto()
    INT = auto()
    FLOAT = auto()


@dataclass
class AtomicType(AbstractType):
    typ: Atomic

    def __str__(self):
        return self.typ


@dataclass
class SetType(AbstractType):
    typ: AbstractType

    def __str__(self):
        return f'set of {self.typ}'


@dataclass
class ArrayType(AbstractType):
    domain: AbstractType
    item: AbstractType

    def __str__(self):
        return f'array[{self.domain}] of {self.item}'


@dataclass
class VarType(AbstractType):
    typ: AbstractType

    def __str__(self):
        return f'var {self.typ}'


@dataclass
class AbstractExpr(ABC):
    pass


@dataclass
class Ident(AbstractExpr):
    id: str

    def __str__(self):
        return self.id


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
    val: str

    def __str__(self):
        return self.val


@dataclass
class SetLiteral(AbstractExpr):
    members: list[AbstractExpr] = field(default_factory=list)

    def __str__(self):
        return f'{{{fmt_list(self.members)}}}'


@dataclass
class ArrayLiteral(AbstractExpr):
    members: list[AbstractExpr] = field(default_factory=list)

    def __str__(self):
        return f'[{fmt_list(self.members)}]'


@dataclass
class CallExpr(AbstractExpr):
    id: Ident
    args: list[AbstractExpr] = field(default_factory=list)

    def __str__(self):
        return f'{self.id}({fmt_list(self.args)})'


@dataclass
class RangeExpr(AbstractExpr):
    lower: AbstractExpr
    upper: AbstractExpr

    def __str__(self):
        return f'{self.lower}..{self.upper}'


@dataclass
class Item(ABC):
    pass


@dataclass
class IncludeItem(Item):
    file: str

    def __str__(self):
        return f'include {self.file}'


@dataclass
class VarDecl:
    typ: AbstractType
    id: Ident

    def __str__(self):
        return f'{self.typ}: {self.id}'


@dataclass
class Annotation():
    ann: list[AbstractExpr] = field(default_factory=list)

    def __str__(self):
        return fmt_list(self.ann, sep=' :: ', at_start=True)


@dataclass
class VarDeclItem(Item):
    vdecl: VarDecl
    ann: Annotation | None = None
    expr: AbstractExpr | None = None

    def __str__(self):
        return f'{self.vdecl}{add_option(self.ann)}{add_option(self.expr, prefix=" = ")}'


@dataclass
class ConstraintItem(Item):
    expr: AbstractExpr
    ann: Annotation | None = None

    def __str__(self):
        return f'constraint {self.expr}{add_option(self.ann)}'


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
class PredicateItem(Item):
    id: Ident
    args: list[VarDecl] = field(default_factory=list)

    def __str__(self):
        return f'predicate {self.id}' + (f'({fmt_list(self.args)})' if self.args else '')


@dataclass
class FlatZincModel:
    items: list[Item] = field(default_factory=list)

    def __str__(self):
        return fmt_list(self.items, sep=';\n') + ';'
