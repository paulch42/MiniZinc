"""
Test suite for the MiniZinc grammar and generation of abstract syntax trees.
Uses the pytest framework.
"""
import pytest
from pyparsing import *
from actions import *


def test_keyword():
    assert keyword.parse_string('ann', parse_all=True)[0] == 'ann'
    assert keyword.parse_string('function', parse_all=True)[0] == 'function'
    assert keyword.parse_string('if', parse_all=True)
    assert keyword.parse_string('record', parse_all=True)
    assert keyword.parse_string('satisfy', parse_all=True)
    assert keyword.parse_string('xor', parse_all=True)
    with pytest.raises(ParseException):
        keyword.parse_string('bol', parse_all=True)


def test_quoted_ident():
    assert quoted_ident.parse_string(
        "'asd!#%&&*'", parse_all=True)[0] == "'asd!#%&&*'"
    assert quoted_ident.parse_string("'-->'", parse_all=True)[0] == "'-->'"
    with pytest.raises(ParseException):
        assert quoted_ident.parse_string("'->'", parse_all=True)[0] == "'->'"
    with pytest.raises(ParseException):
        keyword.parse_string('"wrong quotes"', parse_all=True)


def test_ident():
    assert ident.parse_string('aS43_', parse_all=True)[0].id == 'aS43_'
    assert ident.parse_string('includea', parse_all=True)[0].id == 'includea'
    assert ident.parse_string(
        'ABCDEFGHIJKLMNOPQRSTUVWXYZ4bc3_', parse_all=True)
    assert ident.parse_string(
        '_abcdefghijklmnopqrstuvwxyz0123456789_', parse_all=True)
    assert ident.parse_string("'quoted'", parse_all=True)[0].id == "'quoted'"
    with pytest.raises(ParseException):
        assert ident.parse_string('__abc', parse_all=True)
    with pytest.raises(ParseException):
        assert ident.parse_string('bool', parse_all=True)
    with pytest.raises(ParseException):
        assert ident.parse_string('"data"', parse_all=True)
    with pytest.raises(ParseException):
        ident.parse_string('abc-def', parse_all=True)


def test_anon_var():
    assert isinstance(anon_var.parse_string('_', parse_all=True)[0], AnonVar)


def test_type_variable():
    assert type_variable.parse_string('$$', parse_all=True)[0].id == '$$'
    assert type_variable.parse_string('$ab_34', parse_all=True)[
        0].id == '$ab_34'
    assert type_variable.parse_string('$$XYZ_', parse_all=True)[
        0].id == '$$XYZ_'
    with pytest.raises(ParseException):
        type_variable.parse_string('ABC', parse_all=True)
    with pytest.raises(ParseException):
        type_variable.parse_string('$ ABC', parse_all=True)


def test_atomic_type():
    assert atomic_type.parse_string('bool', parse_all=True)[
        0].typ == Atomic.BOOL
    assert atomic_type.parse_string('int', parse_all=True)[0].typ == Atomic.INT
    assert atomic_type.parse_string('float', parse_all=True)[
        0].typ == Atomic.FLOAT
    assert atomic_type.parse_string('string', parse_all=True)[
        0].typ == Atomic.STRING
    assert atomic_type.parse_string('ann', parse_all=True)[0].typ == Atomic.ANN
    with pytest.raises(ParseException):
        atomic_type.parse_string('array', parse_all=True)
    with pytest.raises(ParseException):
        atomic_type.parse_string('nat', parse_all=True)


def test_any_type():
    x = any_type.parse_string('any', parse_all=True)[0]
    assert isinstance(x, AnyType)
    assert not x.id
    x = any_type.parse_string('any $type_var', parse_all=True)[0]
    assert isinstance(x, AnyType)
    assert x.id.id == '$type_var'
    with pytest.raises(ParseException):
        any_type.parse_string('any id', parse_all=True)
    with pytest.raises(ParseException):
        any_type.parse_string('any $a $b', parse_all=True)


def test_set_type():
    x = set_type.parse_string('set of bool', parse_all=True)[0]
    assert isinstance(x, SetType)
    assert isinstance(x.typ, AtomicType)
    assert x.typ.typ == Atomic.BOOL
    assert set_type.parse_string('set of ann', parse_all=True)
    assert set_type.parse_string('set of opt set of any', parse_all=True)
    assert set_type.parse_string('set of any $abc', parse_all=True)
    with pytest.raises(ParseException):
        set_type.parse_string('set of any bool', parse_all=True)
    with pytest.raises(ParseException):
        set_type.parse_string('set of $abc $123', parse_all=True)


def test_option_type():
    x = option_type.parse_string('opt set of string', parse_all=True)[0]
    assert isinstance(x, OptionType)
    assert isinstance(x.typ, SetType)
    assert option_type.parse_string('opt ann', parse_all=True)
    assert option_type.parse_string('opt any', parse_all=True)
    assert option_type.parse_string('opt set of opt any $abc', parse_all=True)
    with pytest.raises(ParseException):
        option_type.parse_string('opt any bool', parse_all=True)
    with pytest.raises(ParseException):
        option_type.parse_string('opt $abc $123', parse_all=True)


def test_tuple_type():
    x = tuple_type.parse_string('tuple(int,opt float)', parse_all=True)[0]
    assert isinstance(x, TupleType)
    assert len(x.typs) == 2
    assert isinstance(x.typs[0], AtomicType)
    assert isinstance(x.typs[1], OptionType)
    assert tuple_type.parse_string('tuple(int,bool,float)', parse_all=True)
    assert tuple_type.parse_string('tuple(int,bool,float,)', parse_all=True)
    assert tuple_type.parse_string(
        'tuple(any $int,opt bool,set of float,)', parse_all=True)
    with pytest.raises(ParseException):
        assert tuple_type.parse_string(
            'tuple(int,bool,float,,)', parse_all=True)
    with pytest.raises(ParseException):
        assert tuple_type.parse_string(
            'tuple(int,bool float)', parse_all=True)
    with pytest.raises(ParseException):
        assert tuple_type.parse_string(
            'tuple(int,bool,,float)', parse_all=True)


def test_var_decl():
    x = var_decl.parse_string('bool:abc', parse_all=True)[0]
    assert isinstance(x, VarDecl)
    assert isinstance(x.typ, AtomicType)
    assert isinstance(x.id, Ident)
    assert x.id.id == 'abc'
    assert var_decl.parse_string('tuple(bool,$a) : _P23abc', parse_all=True)
    with pytest.raises(ParseException):
        assert var_decl.parse_string(
            'tuple(bool,$a) : $123abc', parse_all=True)
    with pytest.raises(ParseException):
        assert var_decl.parse_string('int;a', parse_all=True)
    with pytest.raises(ParseException):
        assert var_decl.parse_string('int a', parse_all=True)


def test_record_type():
    x = record_type.parse_string(
        'record(int:a,bool:b,float:f)', parse_all=True)[0]
    assert isinstance(x, RecordType)
    assert isinstance(x.vdecls, list)
    assert len(x.vdecls) == 3
    for v in x.vdecls:
        isinstance(v, VarDecl)
    assert record_type.parse_string(
        'record(int:a,tuple(bool,float,):pair,)', parse_all=True)
    assert record_type.parse_string(
        'record(record(int:a,bool:b):rec,)', parse_all=True)
    with pytest.raises(ParseException):
        assert record_type.parse_string('record(int a)', parse_all=True)
    with pytest.raises(ParseException):
        assert record_type.parse_string('rec(int:a)', parse_all=True)
    with pytest.raises(ParseException):
        assert record_type.parse_string('record(int:$a)', parse_all=True)


def test_array_type():
    x = array_type.parse_string(
        'array[string,bool] of float', parse_all=True)[0]
    assert isinstance(x, ArrayType)
    assert len(x.domains) == 2
    assert isinstance(x.titem, AtomicType)
    assert array_type.parse_string(
        'array[tuple(int,int,),abc,] of par opt set of record(int:i,bool:b,)', parse_all=True)
    assert array_type.parse_string('list of float', parse_all=True)
    assert array_type.parse_string(
        'list of par opt set of tuple(var int,par bool,any $x)', parse_all=True)
    with pytest.raises(ParseException):
        assert array_type.parse_string(
            'array[int] of list of tuple(bool,,int)', parse_all=True)
    with pytest.raises(ParseException):
        assert array_type.parse_string(
            'list of list of list of record(bool)', parse_all=True)


def test_var_type():
    x = var_type.parse_string('var set of int', parse_all=True)[0]
    assert isinstance(x, VarType)
    assert isinstance(x.typ, SetType)
    x = var_type.parse_string('par bool', parse_all=True)[0]
    assert isinstance(x, AtomicType)
    x = var_type.parse_string('float', parse_all=True)[0]
    assert isinstance(x, AtomicType)
    with pytest.raises(ParseException):
        assert var_type.parse_string(
            'var par int', parse_all=True)
    with pytest.raises(ParseException):
        assert var_type.parse_string(
            'val int', parse_all=True)


def test_basic_type():
    x = basic_type.parse_string('_ident', parse_all=True)[0]
    assert isinstance(x, Ident)
    assert basic_type.parse_string('float', parse_all=True)
    assert basic_type.parse_string('$type_var4', parse_all=True)
    assert basic_type.parse_string('any $xxx', parse_all=True)
    assert basic_type.parse_string('set of string', parse_all=True)
    assert basic_type.parse_string('opt set of bool', parse_all=True)
    x = basic_type.parse_string('tuple(int,bool)', parse_all=True)[0]
    assert isinstance(x, TupleType)
    assert basic_type.parse_string(
        'record(int:i,bool:b,var float:f)', parse_all=True)
    assert basic_type.parse_string('array[int] of int', parse_all=True)
    assert basic_type.parse_string('list of int', parse_all=True)
    with pytest.raises(ParseException):
        assert basic_type.parse_string('array[int] of int:a', parse_all=True)
    with pytest.raises(ParseException):
        assert basic_type.parse_string('tuple(bool,', parse_all=True)


def test_type_expr():
    assert type_expr.parse_string('bool', parse_all=True)
    x = type_expr.parse_string('bool ++ int', parse_all=True)[0]
    assert isinstance(x, TypeExpr)
    assert isinstance(x.left, AtomicType)
    assert type_expr.parse_string('ann ++ $ab_34', parse_all=True)
    assert type_expr.parse_string(
        'tuple(string) ++ record(string:s)', parse_all=True)
    assert type_expr.parse_string('opt int ++ var float', parse_all=True)
    x = type_expr.parse_string(
        'opt int ++ var float ++ tuple(int,string) ++ array[string] of $abc', parse_all=True)[0]
    assert isinstance(x, TypeExpr)
    assert x.op == BinaryTypeOp.JOIN
    assert isinstance(x.left, OptionType)
    assert isinstance(x.right, TypeExpr)
    assert isinstance(x.right.left, VarType)
    assert isinstance(x.right.right, TypeExpr)
    with pytest.raises(ParseException):
        assert type_expr.parse_string('opt int + var float', parse_all=True)
    with pytest.raises(ParseException):
        assert type_expr.parse_string('opt ++ int', parse_all=True)
    with pytest.raises(ParseException):
        assert type_expr.parse_string('string ++ int ++', parse_all=True)
    with pytest.raises(ParseException):
        assert type_expr.parse_string(
            'int ++ (float ++ string)', parse_all=True)


def test_absent_literal():
    x = absent_literal.parse_string('<>', parse_all=True)[0]
    assert isinstance(x, AbsentLiteral)
    with pytest.raises(ParseException):
        assert absent_literal.parse_string('< >', parse_all=True)


def test_bool_literal():
    x = bool_literal.parse_string('true', parse_all=True)[0]
    assert x.val == Bool.TRUE
    x = bool_literal.parse_string('false', parse_all=True)[0]
    assert x.val == Bool.FALSE
    with pytest.raises(ParseException):
        assert bool_literal.parse_string('True', parse_all=True)


def test_int_literal():
    x = int_literal.parse_string('42', parse_all=True)[0]
    assert x.val == 42
    x = int_literal.parse_string('0x42', parse_all=True)[0]
    assert x.val == 66
    x = int_literal.parse_string('0o42', parse_all=True)[0]
    assert x.val == 34
    with pytest.raises(ParseException):
        assert bool_literal.parse_string('-42', parse_all=True)


def test_float_literal():
    x = float_literal.parse_string('3.14', parse_all=True)[0]
    assert x.val == 3.14
    assert float_literal.parse_string('3.14e10', parse_all=True)
    assert float_literal.parse_string('42E-1000', parse_all=True)
    assert float_literal.parse_string('0xdead.BEEFp4', parse_all=True)
    assert float_literal.parse_string('0xdead.BEEFp4', parse_all=True)
    assert float_literal.parse_string('0x.a1p-4', parse_all=True)
    assert float_literal.parse_string('0xa1.P-40', parse_all=True)
    assert float_literal.parse_string('0xa1.b2P-40', parse_all=True)
    with pytest.raises(ParseException):
        assert float_literal.parse_string('42', parse_all=True)
    with pytest.raises(ParseException):
        assert float_literal.parse_string('-3.14', parse_all=True)


def test_string_literal():
    assert string_literal.parse_string('"abcd"', parse_all=True)
    assert string_literal.parse_string(r'"\(1+2)"', parse_all=True)
    x = string_literal.parse_string(
        r'" The sum of \(1+2) is \(three) . "', parse_all=True)[0]
    assert isinstance(x, StringLiteral)
    assert len(x.strs) == 3
    assert len(x.exprs) == 2
    assert x.strs == [' The sum of ', ' is ', ' . ']
    assert x.exprs[1] == Ident('three')
    assert string_literal.parse_string(r'"   "', parse_all=True)[
        0].strs[0] == '   '
    assert string_literal.parse_string(r'"one embedded \" quote"', parse_all=True)
    assert string_literal.parse_string(r'"nested \"quote\""', parse_all=True)
    assert string_literal.parse_string(r'"coord=(\"\(sin(x))\",\"\(cos(y))\")"', parse_all=True)
    assert string_literal.parse_string('"x % abcd"', parse_all=True)
    assert string_literal.parse_string('"% abcd"', parse_all=True)
    with pytest.raises(ParseException):
        assert string_literal.parse_string(r'"Unescaped " "', parse_all=True)
    with pytest.raises(ParseException):
        assert string_literal.parse_string(r"'wrong quotes'", parse_all=True)


def test_unary_op():
    assert unary_op.parse_string('+', parse_all=True)[0] == '+'
    assert unary_op.parse_string('-', parse_all=True)[0] == '-'
    assert unary_op.parse_string('not', parse_all=True)[0] == 'not'
    with pytest.raises(ParseException):
        assert unary_op.parse_string('^', parse_all=True)


def test_binary_op():
    assert binary_op.parse_string('div', parse_all=True)[0] == 'div'
    assert binary_op.parse_string('<..<', parse_all=True)[0] == '<..<'
    assert binary_op.parse_string('~!=', parse_all=True)[0] == '~!='
    with pytest.raises(ParseException):
        assert binary_op.parse_string('not', parse_all=True)


def test_quoted_op():
    assert quoted_op.parse_string("'symdiff'", parse_all=True)[
        0].op == BinaryOp.SYMDIFF
    assert quoted_op.parse_string(
        "'<->'", parse_all=True)[0].op == BinaryOp.IFF
    assert quoted_op.parse_string(
        r"'/\'", parse_all=True)[0].op == BinaryOp.AND
    with pytest.raises(ParseException):
        assert quoted_op.parse_string("'not'", parse_all=True)
    with pytest.raises(ParseException):
        assert quoted_op.parse_string('"+"', parse_all=True)


def test_expr_seq():
    assert expr_seq.parse_string('true', parse_all=True)
    x = expr_seq.parse_string('true,10,"abcd",', parse_all=True)[0]
    assert isinstance(x, ExprSeq)
    assert len(x.exprs) == 3
    with pytest.raises(ParseException):
        assert expr_seq.parse_string('true;10,"abcd"', parse_all=True)


def test_set_literal():
    x = set_literal.parse_string('{}', parse_all=True)[0]
    assert isinstance(x, SetLiteral)
    assert len(x.members) == 0
    x = set_literal.parse_string('{1,true,"abc",}', parse_all=True)[0]
    assert isinstance(x, SetLiteral)
    assert len(x.members) == 3
    assert x.members[0].val == 1
    assert x.members[1].val
    assert x.members[2].strs[0] == 'abc'
    with pytest.raises(ParseException):
        assert set_literal.parse_string('[]', parse_all=True)
    with pytest.raises(ParseException):
        assert set_literal.parse_string('"{1,2"', parse_all=True)
    with pytest.raises(ParseException):
        assert set_literal.parse_string('{bool}', parse_all=True)


def test_condition():
    assert condition.parse_string('where {}', parse_all=True)


def test_generator():
    assert generator.parse_string('x in [1,2,3]', parse_all=True)
    assert generator.parse_string('x,y,z in [1,2,3]', parse_all=True)
    assert generator.parse_string('x,y in [1,2,3] where true', parse_all=True)
    with pytest.raises(ParseException):
        assert generator.parse_string('x in bool', parse_all=True)
    with pytest.raises(ParseException):
        assert generator.parse_string('x,y in [1,2,3] if true', parse_all=True)


def test_set_comp():
    assert set_comp.parse_string('{ x | x in {}}', parse_all=True)
    assert set_comp.parse_string('{ x | x in {}}', parse_all=True)
    assert set_comp.parse_string('{ x+y | x,y in {}}', parse_all=True)
    assert set_comp.parse_string(
        '{ x+y | x,y in {} where b, z in[1,2,3] where q}', parse_all=True)
    with pytest.raises(ParseException):
        assert set_comp.parse_string('{ x for x in {}}', parse_all=True)
    with pytest.raises(ParseException):
        assert set_comp.parse_string('{ x | x in {} if false}', parse_all=True)


def test_array_literal():
    x = array_literal.parse_string('[]', parse_all=True)[0]
    assert isinstance(x, ArrayLiteral)
    assert len(x.members) == 0
    x = array_literal.parse_string('[1,true,"abc",]', parse_all=True)[0]
    assert isinstance(x, ArrayLiteral)
    assert len(x.members) == 3
    assert x.members[0].val == 1
    assert x.members[1].val
    assert x.members[2].strs[0] == 'abc'
    with pytest.raises(ParseException):
        assert array_literal.parse_string('{}', parse_all=True)
    with pytest.raises(ParseException):
        assert array_literal.parse_string('"[1,2"', parse_all=True)
    with pytest.raises(ParseException):
        assert array_literal.parse_string('[bool]', parse_all=True)


def test_array_literal_2d():
    x = array_literal_2d.parse_string('[| |]', parse_all=True)[0]
    assert isinstance(x, ArrayLiteral2D)
    x = array_literal_2d.parse_string('[| a |]', parse_all=True)[0]
    assert isinstance(x, ArrayLiteral2D)
    x = array_literal_2d.parse_string('[| a| |]', parse_all=True)[0]
    assert isinstance(x, ArrayLiteral2D)
    x = array_literal_2d.parse_string('[| a,b|]', parse_all=True)[0]
    assert isinstance(x, ArrayLiteral2D)
    x = array_literal_2d.parse_string('[| a, |]', parse_all=True)[0]
    assert isinstance(x, ArrayLiteral2D)
    x = array_literal_2d.parse_string(
        '[| a,b,c | 1,2,3 | true,false,"other" |]', parse_all=True)[0]
    assert isinstance(x, ArrayLiteral2D)
    assert len(x.members) == 3
    assert len(x.members[1]) == 3
    assert x.members[1][1] == IntLiteral(2)
    with pytest.raises(ParseException):
        assert array_literal_2d.parse_string('[| | |]', parse_all=True)
    with pytest.raises(ParseException):
        assert array_literal_2d.parse_string('[| a| | |]', parse_all=True)


def test_array_comp():
    assert array_comp.parse_string('[ x | x in {}]', parse_all=True)
    assert array_comp.parse_string('[ x | x in {}]', parse_all=True)
    assert array_comp.parse_string('[ x+y | x,y in {}]', parse_all=True)
    assert array_comp.parse_string(
        '[ x+y | x,y in {} where b, z in [1,2,3] where q]', parse_all=True)
    with pytest.raises(ParseException):
        assert array_comp.parse_string('{[ for x in {}]', parse_all=True)
    with pytest.raises(ParseException):
        assert array_comp.parse_string(
            '[ x | x in {} if false]', parse_all=True)


def test_tuple_index():
    assert tuple_index.parse_string('1', parse_all=True)
    assert tuple_index.parse_string('A', parse_all=True)
    assert tuple_index.parse_string('(1,2)', parse_all=True)


def test_indexed_expr():
    assert indexed_expr.parse_string('1:2', parse_all=True)
    assert indexed_expr.parse_string('A:0', parse_all=True)
    assert indexed_expr.parse_string('(8,9):2', parse_all=True)
    assert indexed_expr.parse_string('0: A,B, C', parse_all=True)


def test_indexed_array_literal():
    assert indexed_array_literal.parse_string('[1:1]', parse_all=True)
    assert indexed_array_literal.parse_string('[A:2]', parse_all=True)
    assert indexed_array_literal.parse_string('[(8,9):2]', parse_all=True)
    assert indexed_array_literal.parse_string('[0: A,B, C]', parse_all=True)
    assert indexed_array_literal.parse_string('[A:0,B:3,C:5]', parse_all=True)
    assert indexed_array_literal.parse_string('[(1,2):1, (1,3):2, (2,2):3, (2,3):4]', parse_all=True)


def test_indexed_array_literal_2d():
    assert indexed_array_literal_2d.parse_string('[| |]', parse_all=True)
    assert indexed_array_literal_2d.parse_string('[| A: B: C: | |]', parse_all=True)
    assert indexed_array_literal_2d.parse_string('[| 1,2,3 |]', parse_all=True)
    assert indexed_array_literal_2d.parse_string('[| X: 1,2,3 |]', parse_all=True)
    assert indexed_array_literal_2d.parse_string('[| X:1 |]', parse_all=True)
    assert indexed_array_literal_2d.parse_string('[| A: B: C: | 0,0,0 | 1,1,1 | 2,2,2 |]', parse_all=True)
    assert indexed_array_literal_2d.parse_string('[| A: 0,0,0 | B: 1,1,1 | C: 2,2,2 |]', parse_all=True)
    assert indexed_array_literal_2d.parse_string('[| A: B: C: | A: 0,0,0 | B: 1,1,1 | C: 2,2,2 |]', parse_all=True)
    assert indexed_array_literal_2d.parse_string('[| 1,2,3 | 4,5,6 |]', parse_all=True)
    with pytest.raises(ParseException):
        assert indexed_array_literal_2d.parse_string('[| A: B: 1 |]', parse_all=True)
    with pytest.raises(ParseException):
        assert indexed_array_literal_2d.parse_string('[| A: B: C: | D: E: F: | |]', parse_all=True)
    with pytest.raises(ParseException):
        assert indexed_array_literal_2d.parse_string('[| 1,2,3 | D: E: F: | |]', parse_all=True)


def test_indexed_array_comp():
    assert indexed_array_comp.parse_string('[i: 3*i | i in 3..5]', parse_all=True)
    assert indexed_array_comp.parse_string('[(i,j): i*3+j | i in 2..4, j in 1..3]', parse_all=True)


def test_tuple_literal():
    assert tuple_literal.parse_string('(1,)', parse_all=True)
    x = tuple_literal.parse_string('(1,false,{})', parse_all=True)[0]
    assert isinstance(x, TupleLiteral)
    assert len(x.members) == 3
    with pytest.raises(ParseException):
        assert tuple_literal.parse_string('()', parse_all=True)
    with pytest.raises(ParseException):
        assert tuple_literal.parse_string('(1,,)', parse_all=True)


def test_labelled_expr():
    assert labelled_expr.parse_string('fst:(1,{2,3},[4,5])', parse_all=True)
    with pytest.raises(ParseException):
        assert labelled_expr.parse_string('snd:bool', parse_all=True)


def test_record_literal():
    assert record_literal.parse_string('(fst:1,)', parse_all=True)
    assert record_literal.parse_string(
        '(nested:(x:2.5,y:7.73))', parse_all=True)
    x = record_literal.parse_string(
        '(fst:1,snd:(1.2,false),third:{<>,2})', parse_all=True)[0]
    assert isinstance(x, RecordLiteral)
    assert len(x.members) == 3
    assert isinstance(x.members[0], LabelledExpr)
    with pytest.raises(ParseException):
        assert record_literal.parse_string('(fst;1)', parse_all=True)


def test_conditional_expr():
    assert conditional_expr.parse_string('if a then b endif', parse_all=True)
    assert conditional_expr.parse_string(
        'if a then b else c endif', parse_all=True)
    assert conditional_expr.parse_string(
        'if a then b elseif c then d endif', parse_all=True)
    assert conditional_expr.parse_string(
        'if a then b elseif c then d else e endif', parse_all=True)
    with pytest.raises(ParseException):
        assert conditional_expr.parse_string('if a then b', parse_all=True)
    with pytest.raises(ParseException):
        assert conditional_expr.parse_string(
            'if a then b elif c then d else e endif', parse_all=True)


def test_let_expr():
    assert let_expr.parse_string('let {int:a} in a', parse_all=True)
    assert let_expr.parse_string(
        'let {int:a;var bool:b;} in if b then a else a+1 endif', parse_all=True)
    assert let_expr.parse_string(
        'let {int:a;constraint true} in a', parse_all=True)
    with pytest.raises(ParseException):
        assert let_expr.parse_string('let int:a in a', parse_all=True)
    with pytest.raises(ParseException):
        assert let_expr.parse_string('let {int:a,bool:b} in a', parse_all=True)
    with pytest.raises(ParseException):
        assert let_expr.parse_string(
            'let {int:a;bool:b} in a endlet', parse_all=True)


def test_call_expr():
    assert call_expr.parse_string('f(1)', parse_all=True)
    assert call_expr.parse_string('f(1,)', parse_all=True)
    assert call_expr.parse_string('f(1,true,a,[])', parse_all=True)
    assert call_expr.parse_string("'quoted'(1)", parse_all=True)
    assert call_expr.parse_string('f(len([1,2,3,],))', parse_all=True)
    with pytest.raises(ParseException):
        assert call_expr.parse_string('f()', parse_all=True)
    with pytest.raises(ParseException):
        assert call_expr.parse_string('f(len([1,2,3,]}', parse_all=True)


def test_call_comp_expr():
    assert call_comp_expr.parse_string('forall(x in [])(x=1)', parse_all=True)
    assert call_comp_expr.parse_string(
        'exists(x,y in [], p in {} where p=2)(x=1)', parse_all=True)
    assert call_comp_expr.parse_string(
        "'oneof'(x, in [])(x=1)", parse_all=True)
    with pytest.raises(ParseException):
        assert call_comp_expr.parse_string('forall(x)(x=1)', parse_all=True)
    with pytest.raises(ParseException):
        assert call_comp_expr.parse_string('forall(x in [])', parse_all=True)


def test_basic_expr():
    assert basic_expr.parse_string('(1+2)', parse_all=True)
    assert basic_expr.parse_string('<>', parse_all=True)
    assert basic_expr.parse_string('true', parse_all=True)
    assert basic_expr.parse_string('3.12', parse_all=True)
    assert basic_expr.parse_string('42', parse_all=True)
    assert basic_expr.parse_string('"asd"', parse_all=True)
    assert basic_expr.parse_string('{}', parse_all=True)
    assert basic_expr.parse_string('{x|x in {}}', parse_all=True)
    assert basic_expr.parse_string('[1,2,3]', parse_all=True)
    assert basic_expr.parse_string('[| 1,2 | 3,4 |]', parse_all=True)
    assert basic_expr.parse_string('[ g | g in []]', parse_all=True)
    assert basic_expr.parse_string('(1,2,3)', parse_all=True)
    assert basic_expr.parse_string('(fst:1,snd:2)', parse_all=True)
    with pytest.raises(ParseException):
        assert basic_expr.parse_string('1+2', parse_all=True)


def test_qualified_expr():
    assert qualified_expr.parse_string('a[3]', parse_all=True)
    assert qualified_expr.parse_string('a.2', parse_all=True)
    assert qualified_expr.parse_string('a[1].4[99]', parse_all=True)
    assert qualified_expr.parse_string('(1+2).d', parse_all=True)
    with pytest.raises(ParseException):
        assert qualified_expr.parse_string('a.div', parse_all=True)


def test_annotated_expr():
    assert annotated_expr.parse_string('[p] :: "abc"', parse_all=True)
    assert annotated_expr.parse_string('f(a) :: 1 :: 2', parse_all=True)
    assert annotated_expr.parse_string('[1,2,3]', parse_all=True)
    assert annotated_expr.parse_string(
        'sum([1,2,3]) :: (f(a) :: 5) :: 9', parse_all=True)
    with pytest.raises(ParseException):
        assert annotated_expr.parse_string('2 : "abc"', parse_all=True)
    with pytest.raises(ParseException):
        assert annotated_expr.parse_string('not p : "abc"', parse_all=True)


def test_unary_expr():
    assert unary_expr.parse_string('+ 24', parse_all=True)
    assert unary_expr.parse_string('-24', parse_all=True)
    assert unary_expr.parse_string('(not p) :: "annotation"', parse_all=True)
    assert unary_expr.parse_string('not p :: "annotation"', parse_all=True)
    assert unary_expr.parse_string('+(4-5)', parse_all=True)
    assert unary_expr.parse_string('+ - not (4-5)', parse_all=True)
    assert unary_expr.parse_string('4 :: true', parse_all=True)
    with pytest.raises(ParseException):
        assert unary_expr.parse_string('~p', parse_all=True)


def test_default_expr():
    assert default_expr.parse_string('1 default 2', parse_all=True)
    assert default_expr.parse_string('not p default not q', parse_all=True)
    assert default_expr.parse_string('not (p default not q)', parse_all=True)
    assert default_expr.parse_string(
        'p :: 1 default q :: 2 :: 3', parse_all=True)
    assert default_expr.parse_string('not p', parse_all=True)
    with pytest.raises(ParseException):
        assert default_expr.parse_string('1 else 2', parse_all=True)
    with pytest.raises(ParseException):
        assert default_expr.parse_string('bool default 4', parse_all=True)
    with pytest.raises(ParseException):
        assert default_expr.parse_string('x ++ y', parse_all=True)


def test_join_expr():
    assert join_expr.parse_string('[] ++ [2,3,4]', parse_all=True)
    x = join_expr.parse_string(
        '[] ++ [2,3,4] ++ f(a) ++ {p|q in {}}', parse_all=True)[0]
    assert isinstance(x, BinaryExpr)
    assert x.op == BinaryOp.JOIN
    assert isinstance(x.left, ArrayLiteral)
    assert isinstance(x.right, BinaryExpr)
    x = join_expr.parse_string(
        '([] ++ [2,3,4] ++ f(a)) ++ {p|q in [1,2,3]}', parse_all=True)[0]
    assert isinstance(x, BinaryExpr)
    assert x.op == BinaryOp.JOIN
    assert isinstance(x.left, BinaryExpr)
    assert x.left.op == BinaryOp.JOIN
    assert isinstance(x.right, SetComp)
    assert join_expr.parse_string('[2,3,4]', parse_all=True)
    with pytest.raises(ParseException):
        assert join_expr.parse_string('[] ++ ', parse_all=True)
    with pytest.raises(ParseException):
        assert join_expr.parse_string('x^y', parse_all=True)


def test_pow_expr():
    assert pow_expr.parse_string('x^y', parse_all=True)
    assert pow_expr.parse_string('2^3^4', parse_all=True)
    assert pow_expr.parse_string('2^(3^4)', parse_all=True)
    assert pow_expr.parse_string('2::a^(3::b^-4::c)', parse_all=True)
    assert pow_expr.parse_string('x++y', parse_all=True)
    with pytest.raises(ParseException):
        assert join_expr.parse_string('2^^3', parse_all=True)


def test_product_expr():
    assert product_expr.parse_string('x*y', parse_all=True)
    assert product_expr.parse_string('x/y', parse_all=True)
    assert product_expr.parse_string('x~*y', parse_all=True)
    assert product_expr.parse_string('x~/y', parse_all=True)
    assert product_expr.parse_string('x div y', parse_all=True)
    assert product_expr.parse_string('x mod y', parse_all=True)
    assert product_expr.parse_string('x~div y', parse_all=True)
    assert product_expr.parse_string('x*y/z mod 42 div 15', parse_all=True)
    assert product_expr.parse_string('x^y', parse_all=True)
    with pytest.raises(ParseException):
        assert product_expr.parse_string('x DIV y', parse_all=True)
    with pytest.raises(ParseException):
        assert product_expr.parse_string('x // y', parse_all=True)
    with pytest.raises(ParseException):
        assert product_expr.parse_string('x ~mod y', parse_all=True)
    with pytest.raises(ParseException):
        assert product_expr.parse_string('x + y', parse_all=True)


def test_sum_expr():
    assert sum_expr.parse_string('x+y', parse_all=True)
    x = sum_expr.parse_string('x+y+z', parse_all=True)[0]
    assert isinstance(x, BinaryExpr)
    assert x.op == BinaryOp.PLUS
    assert isinstance(x.left, BinaryExpr)
    assert isinstance(x.right, Ident)
    x = sum_expr.parse_string('x+(y+z)', parse_all=True)[0]
    assert isinstance(x, BinaryExpr)
    assert x.op == BinaryOp.PLUS
    assert isinstance(x.left, Ident)
    assert isinstance(x.right, BinaryExpr)
    assert sum_expr.parse_string('x-y', parse_all=True)
    assert sum_expr.parse_string('x~+y', parse_all=True)
    assert sum_expr.parse_string('x~-y', parse_all=True)
    assert sum_expr.parse_string('x~++y', parse_all=True)
    assert sum_expr.parse_string('x+y-z~+q', parse_all=True)
    assert sum_expr.parse_string('x*y', parse_all=True)
    with pytest.raises(ParseException):
        assert sum_expr.parse_string('x ~~+ y', parse_all=True)
    with pytest.raises(ParseException):
        assert sum_expr.parse_string('x..y', parse_all=True)


def test_range_expr():
    assert range_expr.parse_string('x..y', parse_all=True)
    assert range_expr.parse_string('x<..y', parse_all=True)
    assert range_expr.parse_string('x..<y', parse_all=True)
    assert range_expr.parse_string('x<..<y', parse_all=True)
    assert range_expr.parse_string('x+1', parse_all=True)
    with pytest.raises(ParseException):
        assert range_expr.parse_string('x..y..z', parse_all=True)
    with pytest.raises(ParseException):
        assert range_expr.parse_string('x<.<y', parse_all=True)
    with pytest.raises(ParseException):
        assert range_expr.parse_string('x intersect y', parse_all=True)


def test_intersect_expr():
    assert intersect_expr.parse_string('{1,2} intersect {2,3}', parse_all=True)
    assert intersect_expr.parse_string(
        '{1,2} intersect {2,3} intersect {x|x in []}', parse_all=True)
    assert intersect_expr.parse_string('{1,2}', parse_all=True)
    with pytest.raises(ParseException):
        assert intersect_expr.parse_string('x inter y', parse_all=True)
    with pytest.raises(ParseException):
        assert intersect_expr.parse_string('x diff y', parse_all=True)


def test_set_op_expr():
    assert set_op_expr.parse_string('x union y', parse_all=True)
    assert set_op_expr.parse_string('x diff y', parse_all=True)
    assert set_op_expr.parse_string('x symdiff y', parse_all=True)
    assert set_op_expr.parse_string(
        'x union y diff z symdiff q', parse_all=True)
    assert set_op_expr.parse_string('x intersect y', parse_all=True)
    with pytest.raises(ParseException):
        assert set_op_expr.parse_string(r'x \ y', parse_all=True)
    with pytest.raises(ParseException):
        assert set_op_expr.parse_string(r'x subset y', parse_all=True)


def test_set_test_expr():
    assert set_test_expr.parse_string('x in y', parse_all=True)
    assert set_test_expr.parse_string('x subset y', parse_all=True)
    assert set_test_expr.parse_string('x superset y', parse_all=True)
    assert set_test_expr.parse_string('x union y', parse_all=True)
    assert set_test_expr.parse_string('p in x union y', parse_all=True)
    with pytest.raises(ParseException):
        assert set_test_expr.parse_string('x in y subset z', parse_all=True)
    with pytest.raises(ParseException):
        assert set_test_expr.parse_string('x != z', parse_all=True)


def test_eq_expr():
    assert eq_expr.parse_string('x == y', parse_all=True)
    assert eq_expr.parse_string('x = y', parse_all=True)
    assert eq_expr.parse_string('x != y', parse_all=True)
    assert eq_expr.parse_string('x ~= y', parse_all=True)
    assert eq_expr.parse_string('x ~!= y', parse_all=True)
    assert eq_expr.parse_string('x in y', parse_all=True)
    with pytest.raises(ParseException):
        assert eq_expr.parse_string('x = y != z', parse_all=True)
    with pytest.raises(ParseException):
        assert eq_expr.parse_string('x < y', parse_all=True)


def test_ineq_expr():
    assert ineq_expr.parse_string('x < y', parse_all=True)
    assert ineq_expr.parse_string('x <= y', parse_all=True)
    assert ineq_expr.parse_string('x >= y', parse_all=True)
    assert ineq_expr.parse_string('x > y', parse_all=True)
    assert ineq_expr.parse_string('x == y', parse_all=True)
    with pytest.raises(ParseException):
        assert ineq_expr.parse_string('x <= y < z', parse_all=True)
    with pytest.raises(ParseException):
        assert ineq_expr.parse_string(r'x /\ y', parse_all=True)


def test_and_expr():
    assert and_expr.parse_string(r'x /\ y', parse_all=True)
    assert and_expr.parse_string(r'x /\ y /\ z', parse_all=True)
    assert and_expr.parse_string(r'x >= y', parse_all=True)
    with pytest.raises(ParseException):
        assert ineq_expr.parse_string(r'x \/z', parse_all=True)


def test_or_expr():
    assert or_expr.parse_string(r'x \/ y', parse_all=True)
    assert or_expr.parse_string(r'x xor y', parse_all=True)
    assert or_expr.parse_string(r'x \/ y xor z', parse_all=True)
    assert or_expr.parse_string(r'x /\ y', parse_all=True)
    with pytest.raises(ParseException):
        assert or_expr.parse_string(r'x -> z', parse_all=True)


def test_iff_expr():
    assert iff_expr.parse_string(r'x -> y', parse_all=True)
    assert iff_expr.parse_string(r'x <- y', parse_all=True)
    assert iff_expr.parse_string(r'x <- y -> z <- p', parse_all=True)
    assert iff_expr.parse_string(r'x xor y', parse_all=True)
    with pytest.raises(ParseException):
        assert iff_expr.parse_string(r'x <-> z', parse_all=True)


def test_binary_expr():
    assert binary_expr.parse_string(r'x <-> y', parse_all=True)
    assert binary_expr.parse_string(r'x <-> y <-> z', parse_all=True)
    assert binary_expr.parse_string(r'x <- y', parse_all=True)
    with pytest.raises(ParseException):
        assert binary_expr.parse_string(r'x <=> y', parse_all=True)


def test_enum_list():
    assert enum_list.parse_string(r'{N}', parse_all=True)
    assert enum_list.parse_string(r'{N,S,E,W,}', parse_all=True)
    assert enum_list.parse_string(r"{'lo','hi'}", parse_all=True)
    with pytest.raises(ParseException):
        assert enum_list.parse_string(r'{}', parse_all=True)
    with pytest.raises(ParseException):
        assert enum_list.parse_string(r'[A,B,C]', parse_all=True)
    with pytest.raises(ParseException):
        assert enum_list.parse_string(r'{1,2,3}', parse_all=True)
    with pytest.raises(ParseException):
        assert enum_list.parse_string(r"{'xor'}", parse_all=True)


def test_enum_anon():
    assert enum_anon.parse_string(r'_(A..Z)', parse_all=True)
    assert enum_anon.parse_string(r'anon_enum(1+2+3)', parse_all=True)
    with pytest.raises(ParseException):
        assert enum_anon.parse_string(r"__(A)", parse_all=True)
    with pytest.raises(ParseException):
        assert enum_anon.parse_string(r"anon(A)", parse_all=True)
    with pytest.raises(ParseException):
        assert enum_anon.parse_string(r"_(A,B,C)", parse_all=True)


def test_enum_construnt():
    assert enum_construct.parse_string(r'A(B)', parse_all=True)
    assert enum_construct.parse_string(r"'name'('arg')", parse_all=True)
    with pytest.raises(ParseException):
        assert enum_construct.parse_string(r"'=='(A)", parse_all=True)
    with pytest.raises(ParseException):
        assert enum_construct.parse_string(r'F(X,Y)', parse_all=True)
    with pytest.raises(ParseException):
        assert enum_construct.parse_string(r'A(1+2)', parse_all=True)


def test_enum_cases():
    assert enum_cases.parse_string(r'{N,S,E,W,}', parse_all=True)
    assert enum_cases.parse_string(r'_(A..Z)', parse_all=True)
    assert enum_cases.parse_string(r'A(B)', parse_all=True)
    with pytest.raises(ParseException):
        assert enum_cases.parse_string(r'_{A}', parse_all=True)


def test_include_item():
    assert include_item.parse_string('include "puzzle.mzn"', parse_all=True)
    assert include_item.parse_string('include "data.dzn"', parse_all=True)
    with pytest.raises(ParseException):
        assert include_item.parse_string("include 'model.mzn'", parse_all=True)
    with pytest.raises(ParseException):
        assert include_item.parse_string('import "data.dzn"', parse_all=True)


def test_var_decl_item():
    assert var_decl_item.parse_string(
        'tuple(bool,$a) : _z23abc', parse_all=True)
    assert var_decl_item.parse_string('any : _L23abc', parse_all=True)
    assert var_decl_item.parse_string(
        'tuple(bool,$a) : _A23abc = 1+2', parse_all=True)
    assert var_decl_item.parse_string('any $A: _Q123abc = 1', parse_all=True)
    assert var_decl_item.parse_string(
        'tuple(bool,$a) : _j23abc :: "test" = {x | x in 1..23 where x div 2 = 0}', parse_all=True)
    assert var_decl_item.parse_string('any : _abc123 :: "ann"', parse_all=True)
    with pytest.raises(ParseException):
        assert var_decl_item.parse_string(
            'tuple(bool,$a) : $123abc', parse_all=True)
    with pytest.raises(ParseException):
        assert var_decl_item.parse_string('any : _qq23abc =', parse_all=True)
    with pytest.raises(ParseException):
        assert var_decl_item.parse_string(
            'tuple(bool,$a)  _123abc', parse_all=True)


def test_enum_item():
    assert enum_item.parse_string('enum Colour', parse_all=True)
    assert enum_item.parse_string('enum Colour :: annotatio', parse_all=True)
    assert enum_item.parse_string('enum Colour = {R,G,B}', parse_all=True)
    assert enum_item.parse_string(
        'enum Colour = {R,G,B}++{C,M,Y,K}', parse_all=True)
    assert enum_item.parse_string(
        'enum Colour :: 42 = _(4)++anon_enum(5)++A(B)', parse_all=True)
    with pytest.raises(ParseException):
        assert enum_item.parse_string('enm Colour', parse_all=True)
    with pytest.raises(ParseException):
        assert enum_item.parse_string('enum Colour {R,G,B}', parse_all=True)
    with pytest.raises(ParseException):
        assert enum_item.parse_string('enum Colour = [R,G,B]', parse_all=True)
    with pytest.raises(ParseException):
        assert enum_item.parse_string(
            'enum Colour = {R,G,B}+{C,M,Y,K}', parse_all=True)


def test_type_synonym_item():
    assert type_synonym_item.parse_string(
        'type Coordinate = tuple(float,float)', parse_all=True)
    assert type_synonym_item.parse_string(
        'type Coordinate :: "annotation" :: 1 = record(var float:x,par opt float:y,)', parse_all=True)
    with pytest.raises(ParseException):
        assert type_synonym_item.parse_string(
            'type Coordinate == tuple(float,float)', parse_all=True)
    with pytest.raises(ParseException):
        assert type_synonym_item.parse_string(
            'type Coordinate = tupl(float,float)', parse_all=True)


def test_assign_item():
    assert assign_item.parse_string('grid = true', parse_all=True)
    assert assign_item.parse_string("'quoted' = [1,2,a]", parse_all=True)
    assert assign_item.parse_string(
        r's = sum(x in y<..<z)(y <= z /\ y = z)', parse_all=True)
    with pytest.raises(ParseException):
        assert assign_item.parse_string('x == y', parse_all=True)
    with pytest.raises(ParseException):
        assert assign_item.parse_string('x = bool', parse_all=True)
    with pytest.raises(ParseException):
        assert assign_item.parse_string("'default' = 5", parse_all=True)


def test_string_annotation():
    assert string_annotation.parse_string(':: "A_1.t"', parse_all=True)
    assert string_annotation.parse_string(
        ':: "string literal"', parse_all=True)
    with pytest.raises(ParseException):
        assert string_annotation.parse_string(
            ': "string literal"', parse_all=True)
    with pytest.raises(ParseException):
        assert string_annotation.parse_string(
            ':: "string literal" :: "not chained"', parse_all=True)
    with pytest.raises(ParseException):
        assert string_annotation.parse_string(': "A_1.t"', parse_all=True)


def test_constraint_item():
    assert constraint_item.parse_string('constraint true', parse_all=True)
    assert constraint_item.parse_string(
        'constraint :: "anno" x < y', parse_all=True)
    with pytest.raises(ParseException):
        assert constraint_item.parse_string(
            'constraint :: "anno"', parse_all=True)
    with pytest.raises(ParseException):
        assert constraint_item.parse_string(
            'constraint :: "anno" :: "anno" false', parse_all=True)
    with pytest.raises(ParseException):
        assert constraint_item.parse_string(
            'constraint : "anno" false', parse_all=True)


def test_solve_item():
    assert solve_item.parse_string('solve satisfy', parse_all=True)
    assert solve_item.parse_string('solve minimize sum', parse_all=True)
    assert solve_item.parse_string(
        'solve maximize min(readings)', parse_all=True)
    assert solve_item.parse_string(
        'solve :: set_search(x) satisfy', parse_all=True)
    assert solve_item.parse_string(
        'solve :: TODO minimize [1,2]', parse_all=True)
    assert solve_item.parse_string('solve :: TODO maximize {}', parse_all=True)
    assert solve_item.parse_string(
        'solve :: anno1 :: anno2 maximize whatever', parse_all=True)
    with pytest.raises(ParseException):
        assert solve_item.parse_string('solve satisfy sum', parse_all=True)
    with pytest.raises(ParseException):
        assert solve_item.parse_string('solve minimize', parse_all=True)
    with pytest.raises(ParseException):
        assert solve_item.parse_string(
            'solve : anno maximize value', parse_all=True)


def test_output_item():
    assert output_item.parse_string('output "abc"', parse_all=True)
    assert output_item.parse_string(
        'output :: "annotation" "abc"++"def"', parse_all=True)
    assert output_item.parse_string('output ["abc"]++["def"]', parse_all=True)
    assert output_item.parse_string(
        r'output "<svg width=\'\((cols+1)*scale)\' height=\'\((rows+1)*scale)\'>\n"', parse_all=True)
    with pytest.raises(ParseException):
        assert output_item.parse_string('output tuple(int)', parse_all=True)
    with pytest.raises(ParseException):
        assert output_item.parse_string('output "a"c"', parse_all=True)
    with pytest.raises(ParseException):
        assert output_item.parse_string('output "a\"c"', parse_all=True)


def test_function_defn():
    assert function_defn.parse_string('f = 1', parse_all=True)
    assert function_defn.parse_string('inc(int:a) = a+1', parse_all=True)
    assert function_defn.parse_string('inc(int:a) :: 4 = a+1', parse_all=True)
    assert function_defn.parse_string(
        'add(int:a,int:b) :: "sum" :: 8 = a+b', parse_all=True)
    assert function_defn.parse_string(
        'add(int:a,int:b) :: "sum" :: 8', parse_all=True)
    assert function_defn.parse_string("'f' :: what = 1", parse_all=True)
    assert function_defn.parse_string(
        'subs(set of int:s,set of int:t) = forall(x in s)(x in t)', parse_all=True)
    with pytest.raises(ParseException):
        assert function_defn.parse_string(
            "'subset'(set of int:s,set of int:t) = forall(x ion s)(x in t)", parse_all=True)


def test_predicate_item():
    assert predicate_item.parse_string(
        'predicate subs(set of int:s,set of int:t) = forall(x in s)(x in t)', parse_all=True)
    assert predicate_item.parse_string(
        'predicate subs(set of int:s,set of int:t)', parse_all=True)
    assert predicate_item.parse_string(
        'predicate subs(set of int:s,set of int:t) :: xyz = forall(x in s)(x in t)', parse_all=True)
    with pytest.raises(ParseException):
        assert predicate_item.parse_string(
            'subs(set of int:s,set of int:t) = forall(x in s)(x in t)', parse_all=True)
    with pytest.raises(ParseException):
        assert predicate_item.parse_string(
            "predicate 'subset'(set of int:s,set of int:t) = forall(x ion s)(x in t)", parse_all=True)


def test_tst_item():
    assert tst_item.parse_string(
        'test subs(set of int:s,set of int:t) = forall(x in s)(x in t)', parse_all=True)
    assert tst_item.parse_string(
        'test subs(set of int:s,set of int:t)', parse_all=True)
    assert tst_item.parse_string(
        'test subs(set of int:s,set of int:t) :: "annotation" = forall(x in s)(x in t)', parse_all=True)
    with pytest.raises(ParseException):
        assert tst_item.parse_string(
            'subs(set of int:s,set of int:t) = forall(x in s)(x in t)', parse_all=True)
    with pytest.raises(ParseException):
        assert tst_item.parse_string(
            "test 'subset'(set of int:s,set of int:t) = forall(x ion s)(x in t)", parse_all=True)


def test_function_item():
    assert function_item.parse_string(
        'function bool: subs(set of int:s,set of int:t) = forall(x in s)(x in t)', parse_all=True)
    assert function_item.parse_string(
        'function bool: subs(set of int:s,set of int:t)', parse_all=True)
    assert function_item.parse_string(
        'function bool: subs(set of int:s,set of int:t) :: 4 = forall(x in s)(x in t)', parse_all=True)
    with pytest.raises(ParseException):
        assert function_item.parse_string(
            'function subs(set of int:s,set of int:t) = forall(x in s)(x in t)', parse_all=True)
    with pytest.raises(ParseException):
        assert function_item.parse_string(
            'subs(set of int:s,set of int:t) = forall(x in s)(x in t)', parse_all=True)
    with pytest.raises(ParseException):
        assert function_item.parse_string(
            "function bool: 'subset'(set of int:s,set of int:t) = forall(x ion s)(x in t)", parse_all=True)


def test_annotation_item():
    assert annotation_item.parse_string(
        'annotation subs(set of int:s,set of int:t) = forall(x in s)(x in t)', parse_all=True)
    with pytest.raises(ParseException):
        assert annotation_item.parse_string(
            'subs(set of int:s,set of int:t) = forall(x in s)(x in t)', parse_all=True)
    with pytest.raises(ParseException):
        assert annotation_item.parse_string(
            "annotation 'subset'(set of int:s,set of int:t) = forall(x ion s)(x in t)", parse_all=True)
    with pytest.raises(ParseException):
        assert annotation_item.parse_string(
            'annotation subs(set of int:s,set of int:t) :: 2 = forall(x in s)(x in t)', parse_all=True)


def test_inline_comment():
    assert inline_comment.parse_string(
        '% hjagd jhgfs kjhs', parse_all=True)
    assert inline_comment.parse_string(
        '  %%%%% hjagd /* jhgfs kjhs', parse_all=True)
    with pytest.raises(ParseException):
        assert inline_comment.parse_string(
            '/* % hjagd jhgfs kjhs', parse_all=True)
    with pytest.raises(ParseException):
        assert inline_comment.parse_string('% abc \nm', parse_all=True)


def test_block_comment():
    assert block_comment.parse_string(
        '/* hjagd jhgfs % kjhs */', parse_all=True)
    assert block_comment.parse_string(
        '   /* jsygd suahf kjhafs\n%jush jghsaef khsf*/', parse_all=True)
    with pytest.raises(ParseException):
        assert block_comment.parse_string(
            '/* % hjagd jhgfs kjhs', parse_all=True)


def test_comment_item():
    assert comment_item.parse_string('% hjagd jhgfs kjhs', parse_all=True)
    assert comment_item.parse_string(
        '   /* jsygd suahf kjhafs\n%jush jghsaef khsf*/', parse_all=True)
    with pytest.raises(ParseException):
        assert block_comment.parse_string('# python comment', parse_all=True)


def test_model_item():
    assert model_item.parse_string('include "file.dzn"', parse_all=True)
    assert model_item.parse_string('var int: a = 4', parse_all=True)
    assert model_item.parse_string('enum abc={A,B,C}', parse_all=True)
    assert model_item.parse_string(
        'type pair = tuple(int,string)', parse_all=True)
    assert model_item.parse_string('point = (x:4.0,y:1.23)', parse_all=True)
    assert model_item.parse_string(
        'constraint forall(x in 1..10)(x < 11)', parse_all=True)
    assert model_item.parse_string('solve satisfy', parse_all=True)
    assert model_item.parse_string(
        r'output ["ABC \(1+2)"] ++ [show(f)]', parse_all=True)
    assert model_item.parse_string(
        'predicate iseven(int:i)= i div 2 = 0', parse_all=True)
    assert model_item.parse_string(
        'test iseven(int:i)= i div 2 = 0', parse_all=True)
    assert model_item.parse_string(
        'function bool: iseven(int:i)= i div 2 = 0', parse_all=True)
    assert model_item.parse_string(
        'annotation iseven(int:i)= i div 2 = 0', parse_all=True)
    assert model_item.parse_string(
        '/* block comment item */', parse_all=True)
    assert model_item.parse_string('% inline comment item', parse_all=True)


def test_minizinc_model():
    assert minizinc_model.parse_string('include "file.dzn";', parse_all=True)
    assert minizinc_model.parse_string(
        'include "file.dzn";var int: a = 4;enum abc={A,B,C};type pair = tuple(int,string);point = (x:4.0,y:1.23);constraint forall(x in 1..10)(x < 11);', parse_all=True)
    assert minizinc_model.parse_string(
        '/* comment 1 */include "file.dzn";/* comment 2*/var int: a = 4;/* comment 3*/', parse_all=True)
    assert minizinc_model.parse_string(
        '% inline 1\ninclude "file.dzn"; % inline 2\nvar int: a = 4; % inline 3', parse_all=True)
    assert minizinc_model.parse_string(
        '% inline 1\ninclude "file.dzn"; % inline 2\nvar int: a = 4 % inline 3', parse_all=True)
    assert minizinc_model.parse_string('include "file.dzn"', parse_all=True)
    with pytest.raises(ParseException):
        assert minizinc_model.parse_string(
            'function bool: /* embedded */ iseven(int:i)= "-%cd" /* again */ div 2 = 0;', parse_all=True)
    with pytest.raises(ParseException):
        assert minizinc_model.parse_string(
            'function bool: iseven(int:i)= % embedded\n "x%as%";', parse_all=True)
    with pytest.raises(ParseException):
        assert minizinc_model.parse_string(
            'function bool: /* embedded */ iseven(int:i)= i /* again */ div 2 = 0;', parse_all=True)
    with pytest.raises(ParseException):
        assert minizinc_model.parse_string(
            'function bool: iseven(int:i)= % embedded\n "  %as%";', parse_all=True)
