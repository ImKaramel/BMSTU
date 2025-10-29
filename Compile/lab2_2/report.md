% Лабораторная работа № 2.2 «Абстрактные синтаксические деревья»
% 24 апреля 2024 г.
% Ольга Александрова, ИУ9-61Б

# Цель работы

Целью данной работы является получение навыков составления грамматик и проектирования
синтаксических деревьев.

# Индивидуальный вариант

Язык L4.
Вложенные комментарии реализовывать не нужно.

# Реализация

## Абстрактный синтаксис

Программа на языке L4 представляет собой набор определений функций
```Program → Func*```

Определение функции состоит из заголовка и тела.
```Func -> Header Body```

Заголовок функции может быть 2-х типов:
 1)возвращающей значение (тип [имя параметры])
 2)не возвращающий значения [имя параметры ]
```Header -> (Type [FuncName FuncArgs]) | [FuncName FuncArgs]```

Список формальных параметров представляет собой последовательность объявлений параметров.

```FuncArgs -> (Type : VarName)+```

Тело функции состоит из последовательности операторов, разделённых запятой и завершается %%
```FuncBody → (Statement , … , Statement | ε) %%```

```Type → INT | CHAR | BOOL | ARRAY | DOUBLE_ARRAY```

Операторы задают действия, выполняемые программой. Всего предусмотрено восемь видов операторов:
оператор-объявление (1,2), оператор присваивания(3), оператор вызова функции (4),
оператор выбора (5,6), два цикла с предусловием (7,8), оператор завершения функции (9)
и оператор-предупреждение (10).

```Statement -> (Type : VarName)
            | (Type : VarName) := Expr
            | Expr := Expr
            | Expr
            | (? Expr) Statement+ %
            | (? Expr) Statement+ +++ Statement+ %
            | (& Expr) Statement+ %
            | ((Type : VarName) : Expr, Expr, Expr*) Statement+ %
            | ^ Expr
            | \ Expr
            | ε
```

Выражения в языке формируются из символов операций, констант, имён переменных,
параметров и функций, изображений типов и круглых скобок.

```Expr -> | Expr BinOp Expr
           | UnOp Expr
           | VarName
           | Const
           | (Expr)
           | SpecOp
           | FUNC_CALL


BinOp → + | - | * | / | MOD | POW |  EQ | NE | LT | GT | LE | GE | AND | OR | XOR

Const → INT_CONST | CHAR_CONST | STRING_CONST | TRUE | FALSE | NULL_REF_CONST

UnOp →  NOT | -

SpecOp → ARRAY_ACCESS | NEW

```

## Лексическая структура и конкретный синтаксис
…

## Программная реализация

```python
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


@dataclass
class MainVar:
    type: Type or MainType
    var_name: Any


class Header(abc.ABC):
    def __init__(self, type: Optional[Type or MainType] = None, funcName: Any = None,
                 funcArgs: list[MainVar] = None):
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
    type: Type
    var_name: Any


@dataclass
class Func:
    header: Header
    body: Body


class Expr(abc.ABC):
    pass


class Statement(abc.ABC):
    pass


class Pattern:
    pass


class PatternUnit:
    pass

@dataclass
class Patterns(Pattern):
    patterns: list[Pattern]


@dataclass
class FuncCall(Expr):
    funcName: Any
    args: Expr

@dataclass
class DeclStatement(Statement):
    variable: MainVar
    expr: Expr or None

@dataclass
class AssignStatement(Statement):
    variable: Any
    expr: Expr


@dataclass
class NewStatement(Statement):
    type: Type
    alloc_size: Any


@dataclass
class NewVarStatement(Statement):
    variable: Any


@dataclass
class IfStatement(Expr):
    condition: Expr
    thenBranch: Statement
    elseBranch: Statement = None


@dataclass
class ForHeader:
    head: CycleVar
    start: Expr
    end: Expr
    step: Any = None


@dataclass
class ArraySearch(Expr):
    array: Expr
    index: Expr


@dataclass
class WhileStatement(Statement):
    condition: Expr
    body: Statement


@dataclass
class ForStatement(Statement):
    head: ForHeader
    body: Statement


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
    
    
@dataclass
class Program:
    funcs: list[Func]


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
NDeclStatement = pe.NonTerminal('DeclStatement')
NCycleStatement = pe.NonTerminal('CycleStatement')
NCycle = pe.NonTerminal('Cycle')
NCycleVar = pe.NonTerminal('CycleVar')
NArgs = pe.NonTerminal('Args')
NLogicalExpr = pe.NonTerminal('LogicalExpr')
NCompareExpr = pe.NonTerminal('CompareExpr')
NFuncBody = pe.NonTerminal('FuncBody')
NCmpOp = pe.NonTerminal('CmpOp')
NArithmExpr = pe.NonTerminal('ArithmExpr')
NFuncs = pe.NonTerminal('Funcs')
NUnOp = pe.NonTerminal('UnOp')
NPowOp= pe.NonTerminal('PowOp')
NAddOp = pe.NonTerminal('AddOp')
NPowExpr = pe.NonTerminal('PowExpr')
NTerm = pe.NonTerminal('Term')
NMulOp = pe.NonTerminal('MulOp')
NUnOpExp = pe.NonTerminal('UnOpExp')
NArrIndex = pe.NonTerminal("ArrIndex")
NSpec = pe.NonTerminal('Spec')
NConst = pe.NonTerminal('Const ')
NVar = pe.NonTerminal('Var')

KW_INT, KW_CHAR, KW_BOOL, KW_XOR, KW_OR, KW_MOD, KW_AND, KW_TRUE, KW_FALSE \
    = construct_terminals('int char bool XOR OR MOD AND TRUE FALSE')

# грамматика
NProgram |= NFuncs, lambda st2: Program(st2)
NFuncs |= NFuncs, NFunc, lambda fncs, fn: fncs + [fn]
NFuncs |= lambda: []

NFunc |= NFuncHeader, NFuncBody, Func
NFuncHeader |= '[', FuncName, NFuncParams, ']', lambda name, params: Header(None, name, params)
NFuncHeader |= '(', NType, '[', FuncName, NFuncParams, ']', ')', Header

NFuncBody |= NStatements, '%%', lambda statements: Body(statements)

NFuncParams |= NMainVar, lambda st1: [st1]
NFuncParams |= NFuncParams, NMainVar, lambda vars, var: vars + [var]

NMainVar |= '(', NType, IDENT, ')', MainVar

NMainType |= KW_INT, lambda: MainType.Integer
NMainType |= KW_CHAR, lambda: MainType.Char
NMainType |= KW_BOOL, lambda: MainType.Boolean

NType |= NMainType
NType |= '<', NType, '>', lambda t: ArrayType(t)

NStatements |= NStatement, lambda st: [st]
NStatements |= NStatements, ',', NStatement, lambda sts, st3: sts + [st3]
NStatement |= '^', NExpr, ReturnStatement
NStatement |= '\\', NExpr, ReturnStatement

NStatement |= NExpr, ':=', NExpr, AssignStatement
NStatement |= NDeclStatement

NDeclStatement |= NMainVar, ':=', NExpr, DeclStatement
NDeclStatement |= NMainVar, DeclStatement

NStatement |= '(', '?', NExpr, ')', NStatements, '+++', NStatements, '%', IfStatement
NStatement |= '(', '?', NExpr, ')', NStatements, '%', IfStatement
NStatement |= NCycleStatement
NCycleStatement |= '(', '&', NExpr, ')', NStatements, '%', lambda expr, states: \
    WhileStatement(expr, states)
NCycleStatement |= NCycle , NStatements, '%', ForStatement

NStatement |= '[', FuncName, NArgs, ']', FuncCall

NArgs |= NSpec, lambda vn: [vn]
NArgs |= NArgs, NSpec, lambda args, arg: args + [arg]

##################

NCycle |= '(', NCycleVar, ':', NExpr, ',', NExpr, ',', INTEGER, ')', ForHeader
NCycle |= '(', NCycleVar, ':', NExpr, ',', NExpr, ')', ForHeader
NCycleVar |= NType, IDENT, CycleVar
#################


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
NPowExpr |= NTerm, NPowOp, NPowExpr, BinExpr

NPowOp |= '_pow_', lambda: '_pow_'

NTerm |= NUnOpExp
NTerm |= NUnOpExp, NMulOp, NTerm, BinExpr

NMulOp |= '*', lambda: '*'
NMulOp |= '/', lambda: '/'
NMulOp |= KW_MOD, lambda: 'mod'

################
# NUnOp |= '-', lambda: '-'
# NUnOp |= 'not_', lambda: 'not_'
NUnOpExp |= 'not_', NSpec, UnExpr
NUnOpExp |= '-', NSpec, UnExpr
NUnOpExp |= '<', NVar, NExpr, '>', BinExpr
NUnOpExp |= NSpec
###################

NSpec |= NFuncCall
NFuncCall |= '[', FuncName, NArgs, ']', FuncCall

NSpec |= 'new_', NType, INTEGER, NewStatement
NSpec |= NConst
NSpec |= NVar
NSpec |= '(', NExpr, ')'

NVar |= IDENT, Var

NConst |= INTEGER, lambda v: ConstExpr(v, MainType.Integer)
NConst |= CHAR, lambda v: ConstExpr(v, MainType.Char)
NConst |= STRING, lambda v: ConstExpr(CharSequenceType(v), ArrayType(MainType.Char))
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


```

# Тестирование

## Входные данные

```
(<int> [SumVectors (<int> !A)
    (<int> !B)]
    )
    (int #size) := [length !A],
    (<int> #C) := new_ <int> 777777F{16},
    !x := !a _eq_ 1,
    #x := #a _pow_ 2,
    <!A 5> := <#B 6> * 10,
    <[Func #x #y] !i+1> := 0,
    [Factorial #x],
    (<int> #P) := new_ <int> 10,
    (<int> #i : 0, #size - 1)
        <#C #i> := <!A #i> + <!B #i>
        { <#C 5> := <!A #i> + <!B #i> }
    %,
    (?#a _lt_ 0)
        #sign := -1
    +++
        (?#a _eq_ 0)
            #sign := 0
        +++
            #sign :=1
        %
    %,
    ^ #C
%%

(int [Factorial (int _n)])
  _n := 1 * _n * [Factorial(_n - 1)],
  ^ #C
%%


(<int> [Main (<<char>> !args)])
   (<int> !A),
   (<int> !B),
   [SumVectors (!A) (!B)],
   (int @a) := 'HELLO WORLD',
    ^ #C
%%

```

## Вывод на `stdout`

<!-- ENABLE LONG LINES -->

```
[Func(header=Header(ArrayType(type=<MainType.Integer: 'int'>), 'SumVectors', [BasicVar(type=ArrayType(type=<MainType.Integer: 'int'>), var_name='!A'), BasicVar(type=ArrayType(type=<MainType.Integer: 'int'>), var_name='!B')]),
      body=[AssignStatement(variable=BasicVar(type=<MainType.Integer: 'int'>,
                                              var_name='#size'),
                            expr=FuncCall(funcName='length',
                                          args=[Var(Name='!A')])),
            AssignStatement(variable=BasicVar(type=ArrayType(type=<MainType.Integer: 'int'>),
                                              var_name='#C'),
                            expr=NewStatement(type=ArrayType(type=<MainType.Integer: 'int'>),
                                              alloc_size='777777F{16}')),
            AssignStatement(variable=Var(Name='!x'),
                            expr=BinExpr(left=Var(Name='!a'),
                                         op='_eq_',
                                         right=ConstExpr(value='1',
                                                         type=<MainType.Integer: 'int'>))),
            AssignStatement(variable=Var(Name='#x'),
                            expr=BinExpr(left=Var(Name='#a'),
                                         op='_pow_',
                                         right=ConstExpr(value='2',
                                                         type=<MainType.Integer: 'int'>))),
            AssignStatement(variable=ArraySearch(array=Var(Name='!A'),
                                                 index=ConstExpr(value='5',
                                                                 type=<MainType.Integer: 'int'>)),
                            expr=BinExpr(left=ArraySearch(array=Var(Name='#B'),
                                                          index=ConstExpr(value='6',
                                                                          type=<MainType.Integer: 'int'>)),
                                         op='*',
                                         right=ConstExpr(value='10',
                                                         type=<MainType.Integer: 'int'>))),
            AssignStatement(variable=ArraySearch(array=FuncCall(funcName='Func',
                                                                args=[Var(Name='#x'),
                                                                      Var(Name='#y')]),
                                                 index=BinExpr(left=Var(Name='!i'),
                                                               op='+',
                                                               right=ConstExpr(value='1',
                                                                               type=<MainType.Integer: 'int'>))),
                            expr=ConstExpr(value='0',
                                           type=<MainType.Integer: 'int'>)),
            FuncCall(funcName='Factorial', args=[Var(Name='#x')]),
            AssignStatement(variable=BasicVar(type=ArrayType(type=<MainType.Integer: 'int'>),
                                              var_name='#P'),
                            expr=NewStatement(type=ArrayType(type=<MainType.Integer: 'int'>),
                                              alloc_size='10')),
            ForStatement(head=ForHeader(head=CycleVar(type=ArrayType(type=<MainType.Integer: 'int'>),
                                                      var_name='#i'),
                                        start=ConstExpr(value='0',
                                                        type=<MainType.Integer: 'int'>),
                                        end=BinExpr(left=Var(Name='#size'),
                                                    op='-',
                                                    right=ConstExpr(value='1',
                                                                    type=<MainType.Integer: 'int'>)),
                                        step=None),
                         body=[AssignStatement(variable=ArraySearch(array=Var(Name='#C'),
                                                                    index=Var(Name='#i')),
                                               expr=BinExpr(left=ArraySearch(array=Var(Name='!A'),
                                                                             index=Var(Name='#i')),
                                                            op='+',
                                                            right=ArraySearch(array=Var(Name='!B'),
                                                                              index=Var(Name='#i'))))]),
            IfStatement(condition=BinExpr(left=Var(Name='#a'),
                                          op='_lt_',
                                          right=ConstExpr(value='0',
                                                          type=<MainType.Integer: 'int'>)),
                        thenBranch=[AssignStatement(variable=Var(Name='#sign'),
                                                    expr=UnExpr(op='-',
                                                                expr=ConstExpr(value='1',
                                                                               type=<MainType.Integer: 'int'>)))],
                        elseBranch=[IfStatement(condition=BinExpr(left=Var(Name='#a'),
                                                                  op='_eq_',
                                                                  right=ConstExpr(value='0',
                                                                                  type=<MainType.Integer: 'int'>)),
                                                thenBranch=[AssignStatement(variable=Var(Name='#sign'),
                                                                            expr=ConstExpr(value='0',
                                                                                           type=<MainType.Integer: 'int'>))],
                                                elseBranch=[AssignStatement(variable=Var(Name='#sign'),
                                                                            expr=ConstExpr(value='1',
                                                                                           type=<MainType.Integer: 'int'>))])]),
            ReturnStatement(expr=Var(Name='#C'))]),
 Func(header=Header(<MainType.Integer: 'int'>, 'Factorial', [BasicVar(type=<MainType.Integer: 'int'>, var_name='_n')]),
      body=[AssignStatement(variable=Var(Name='_n'),
                            expr=BinExpr(left=ConstExpr(value='1',
                                                        type=<MainType.Integer: 'int'>),
                                         op='*',
                                         right=BinExpr(left=Var(Name='_n'),
                                                       op='*',
                                                       right=FuncCall(funcName='Factorial',
                                                                      args=[BinExpr(left=Var(Name='_n'),
                                                                                    op='-',
                                                                                    right=ConstExpr(value='1',
                                                                                                    type=<MainType.Integer: 'int'>))])))),
            ReturnStatement(expr=Var(Name='#C'))]),
 Func(header=Header(ArrayType(type=<MainType.Integer: 'int'>), 'Main', [BasicVar(type=ArrayType(type=ArrayType(type=<MainType.Char: 'char'>)), var_name='!args')]),
      body=[NewVarStatement(variable=BasicVar(type=ArrayType(type=<MainType.Integer: 'int'>),
                                              var_name='!A')),
            NewVarStatement(variable=BasicVar(type=ArrayType(type=<MainType.Integer: 'int'>),
                                              var_name='!B')),
            FuncCall(funcName='SumVectors',
                     args=[Var(Name='!A'), Var(Name='!B')]),
            AssignStatement(variable=BasicVar(type=<MainType.Integer: 'int'>,
                                              var_name='@a'),
                            expr=CharSequenceType("'HELLO WORLD'")),
            ReturnStatement(expr=Var(Name='#C'))])]
```

# Вывод

В результате проделанной работы были получены навыки составления грамматик и проектирования 
синтаксических деревьев. Был разработан синтаксический анализатор на языке Python с использованием 
библиотеки parseredsl.py.

Данная работа позволила более глубоко изучить абстрактные синтаксические деревья и 
их применение в разработке синтаксических анализаторов. 