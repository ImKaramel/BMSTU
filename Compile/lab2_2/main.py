import abc
import enum
import parser_edsl.parser_edsl as pe
import re
from typing import Any, Optional
from typing import List
from dataclasses import dataclass
from pprint import pprint


class Type(abc.ABC):
    pass


class MainType(enum.Enum):
    Char = 'char'
    Integer = 'int'
    Boolean = 'bool'

# class ArrayType(enum.Enum):
#     Char = 'char'
#     Integer = 'int'

@dataclass
class declVar:
    type: Type or MainType
    var_name: Any


class Header(abc.ABC):
    def __init__(self, type: Optional[Type or MainType] = None, funcName: Any = None,
                 funcArgs: list[declVar] = None):
        self.type = type
        self.funcName = funcName
        self.funcArgs = funcArgs

    def __repr__(self):
        return f'Header({self.type!r}, {self.funcName!r}, {self.funcArgs!r})'


class Body(abc.ABC):
    pass


class CharSequenceType(Type):
    def __init__(self, value: str):
        self.value = value

    def __repr__(self):
        return f'CharSequenceType({self.value!r})'


@dataclass
class ArrayType:
    type: Type


@dataclass
class CycleVar:
    type: MainType.Integer or MainType.Char
    var_name: Any


@dataclass
class Func:
    header: Header
    body: Body


class Expr(abc.ABC):
    pass


class Statement(abc.ABC):
    pass


@dataclass
class FuncCall(Expr):
    funcName: Any
    args: Expr


@dataclass
class AssignStatement(Statement):
    variable: Any
    expr: Expr


@dataclass
class NewStatement(Statement):
    type: Type
    allocSize: MainType.Integer


# @dataclass
# class NewVarStatement(Statement):
#     variable: Any


@dataclass
class IfStatement(Expr):
    condition: Expr
    thenBranch: list[Statement]
    elseBranch: list[Statement] = None


@dataclass
class ForStatement:
    type: Type
    name: Any
    start: Expr
    end: Expr
    statements: list[Statement]
    step: MainType.Integer = None


@dataclass
class ArraySearch(Expr):
    array: Expr
    index: Expr


@dataclass
class WhileStatement(Statement):
    condition: Expr
    body: list[Statement]


# @dataclass
# class ForStatement(Statement):
#     head: ForHeader
#     body: Statement


@dataclass
class Var(Expr):
    Name: Any

@dataclass
class ConstExpr(Expr):
    value: Any
    type: Type or MainType


@dataclass
class BinExpr(Expr):
    left: Expr
    op: str
    right: Expr


@dataclass
class UnExpr(Expr):
    op: str
    expr: Expr


@dataclass
class ReturnStatement(Statement):
    expr: Expr


# Лексическая структура

INTEGER = pe.Terminal('INTEGER', r'\b[0-9A-Za-z]+\{[0-9]+\}|\b[0-9]+\b', str, priority=7)

CHAR = pe.Terminal('CHAR', r'"(?:\\[\s\S]|[^\\"])*"|\$[A-Z]+\$|\$[0-9A-Fa-f]+\$', str)

IDENT = pe.Terminal('IDENT', r'[!@.#_][a-zA-Z0-9]*', str)

FuncName = pe.Terminal('FUNCNAME', r'[a-zA-Z0-9]*', str)

STRING = pe.Terminal('STRING', r'\'.*\'', str)

REF_CONST = ('REF_CONST', 'nothing', str)


def construct_terminals(tokens):
    def create_terminal(token):
        return pe.Terminal(token, token, lambda name: None, priority=10)

    return list(map(create_terminal, tokens.split()))


NProgram = pe.NonTerminal('Program')
NFunc = pe.NonTerminal('Func')
NFuncHeader = pe.NonTerminal('FuncHeader')
NFuncParams = pe.NonTerminal('FuncParams')
NMainVar = pe.NonTerminal('MainVar')
NType = pe.NonTerminal('Type')
NMainType = pe.NonTerminal('MainType')
NStatements = pe.NonTerminal('Statements')
NFuncCall = pe.NonTerminal('FuncCall')
NStatement = pe.NonTerminal('Statement')
NExpr = pe.NonTerminal('Expr')
NCycle = pe.NonTerminal('Cycle')
NCycleVar = pe.NonTerminal('CycleVar')
NArgs = pe.NonTerminal('Args')
NLogicalExpr = pe.NonTerminal('LogicalExpr')
NCompareExpr = pe.NonTerminal('CompareExpr')
NFuncBody = pe.NonTerminal('FuncBody')
NCmpOp = pe.NonTerminal('CmpOp')
NArithmExpr = pe.NonTerminal('ArithmExpr')

NPattern = pe.NonTerminal('Pattern')
NPatternUnit = pe.NonTerminal('PatternUnit')
NPatternTuple = pe.NonTerminal('PatternTuple')
NPatternList = pe.NonTerminal('PatternList')

NAddOp = pe.NonTerminal('AddOp')
NPowExpr = pe.NonTerminal('PowExpr')
NTerm = pe.NonTerminal('Term')
NMulOp = pe.NonTerminal('MulOp')
NFactor = pe.NonTerminal('Factor')
NSpec = pe.NonTerminal('Spec')
NConst = pe.NonTerminal('Const ')
NVar = pe.NonTerminal('Var')

KW_INT, KW_CHAR, KW_BOOL, KW_XOR, KW_OR, KW_MOD, KW_AND, KW_TRUE, KW_FALSE \
    = construct_terminals('int char bool XOR OR MOD AND TRUE FALSE')

# грамматика
NProgram |= NFunc, lambda st: [st]
NProgram |= NProgram, NFunc, lambda fncs, fn: fncs + [fn]

NFunc |= NFuncHeader, NFuncBody, lambda h, b: Func(h, b)

NFuncHeader |= '[', FuncName, NFuncParams, ']', lambda name, params: Header(None, name, params)
NFuncHeader |= '(', NType, '[', FuncName, NFuncParams, ']', ')', Header

NFuncBody |= NStatements, '%%'

NFuncParams |= NMainVar, lambda st: [st]
NFuncParams |= NFuncParams, NMainVar, lambda vars, var: vars + [var]

NMainVar |= '(', NType, IDENT, ')', declVar

NType |= NMainType
NType |= '<', NType, '>', ArrayType

NMainType |= KW_INT, lambda: MainType.Integer
NMainType |= KW_CHAR, lambda: MainType.Char
NMainType |= KW_BOOL, lambda: MainType.Boolean

NStatements |= NStatement, lambda st: [st]
NStatements |= NStatements, ',', NStatement, lambda sts, st: sts + [st]

NStatement |= '^', NExpr, ReturnStatement
NStatement |= '\\', NExpr, ReturnStatement

NStatement |= NVar, ':=', NExpr, AssignStatement
NStatement |= NMainVar, ':=', NExpr, AssignStatement

NStatement |= '[', FuncName, NArgs, ']', FuncCall

NStatement |= '(', '?', NExpr, ')', NStatements, '+++', NStatements, '%', IfStatement
NStatement |= '(', '?', NExpr, ')', NStatements, '%', IfStatement
NStatement |= '(', '&', NExpr, ')', NStatements, '%', WhileStatement
NStatement |= NCycle, NStatements, '%', ForStatement


NPatternUnit |= NConst
NPatternUnit |= NPatternList,
NPatternUnit |= NPatternTuple,

NPatternUnit |= '[', NPattern, ']',

NCycle |= '(', NCycleVar, ':', NExpr, ',', NExpr, ',', INTEGER, ')', \
    lambda name, expr1, expr2, statements, step:  ForStatement(Type, name, expr1, expr2,  statements, step)

NCycle |= '(', NCycleVar, ':', NExpr, ',', NExpr, ')', ForHeader
# NCycleVar |= NType, IDENT, CycleVar
# NCycleVar |= IDENT, lambda name: CycleVar(None, name)

NArgs |= NSpec, lambda vn: [vn]
NArgs |= NArgs, NSpec, lambda args, arg: args + [arg]


def make_op_lambda(op):
    return lambda: op


for op in ('_eq_', '_ne_', '_lt_', '_gt_', '_le_', '_ge_'):
    NCmpOp |= op, make_op_lambda(op)

NExpr |= NLogicalExpr
NExpr |= NExpr, KW_OR, NLogicalExpr, BinExpr

NLogicalExpr |= NCompareExpr
NLogicalExpr |= NLogicalExpr, KW_AND, NCompareExpr, BinExpr

NCompareExpr |= NArithmExpr
NCompareExpr |= NArithmExpr, NCmpOp, NArithmExpr, BinExpr

NArithmExpr |= NPowExpr
NArithmExpr |= NPowExpr, NAddOp, NPowExpr, BinExpr

NAddOp |= '+', lambda: '+'
NAddOp |= '-', lambda: '-'

NPowExpr |= NTerm
NPowExpr |= NTerm, '_pow_', NPowExpr, lambda p, f: BinExpr(p, '_pow_', f)

NTerm |= NFactor
NTerm |= NFactor, NMulOp, NTerm, BinExpr

NMulOp |= '*', lambda: '*'
NMulOp |= '/', lambda: '/'
NMulOp |= KW_MOD, lambda: 'mod'

NFactor |= 'not', NSpec, lambda p: UnExpr('not', p)
NFactor |= '-', NSpec, lambda t: UnExpr('-', t)
NFactor |= NSpec

NFuncCall |= '[', FuncName, NArgs, ']', FuncCall

NSpec |= NFuncCall
NSpec |= 'new_', NType, INTEGER, NewStatement
NSpec |= NConst
NSpec |= NVar
NSpec |= '(', NExpr, ')'

NVar |= IDENT, Var
NVar |= '<', NSpec, NExpr, '>', ArraySearch

NConst |= INTEGER, lambda v: ConstExpr(v, MainType.Integer)
NConst |= CHAR, lambda v: ConstExpr(v, MainType.Char)
NConst |= STRING, CharSequenceType

NConst |= KW_TRUE, lambda: ConstExpr(True, MainType.Boolean)
NConst |= KW_FALSE, lambda: ConstExpr(False, MainType.Boolean)

parser = pe.Parser(NProgram)
assert parser.is_lalr_one()
parser.print_table()

parser.add_skipped_domain('\s')

parser.add_skipped_domain('\\{.*?\\}')

filename = "in.txt"
try:
    with open(filename) as f:
        tree = parser.parse(f.read())
        pprint(tree)
except pe.Error as e:
    print(f'Ошибка {e.pos}: {e.message}')
except Exception as e:
    print(e)
