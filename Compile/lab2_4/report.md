% Лабораторная работа № 2.4 «Рекурсивный спуск»
% 17 июня 2024 г.
% Ольга Александрова, ИУ9-61Б

# Цель работы
Целью данной работы является изучение алгоритмов построения парсеров методом рекурсивного спуска.

# Индивидуальный вариант
Язык L4.

## Лексическая структура
```
INTEGER = pe.Terminal('INTEGER', r'\b[0-9A-Za-z]+\{[0-9]+\}|\b[0-9]+\b', str, priority=7)
CHAR = pe.Terminal('CHAR', r'"(?:\\[\s\S]|[^\\"])*"|\$[A-Z]+\$|\$[0-9A-Fa-f]+\$', str)
IDENT = pe.Terminal('IDENT', r'[!@.#_][a-zA-Z0-9]*', str)
FuncName = pe.Terminal('FUNCNAME', r'[a-zA-Z0-9]*', str)
STRING = pe.Terminal('STRING', r'\'.*\'', str)
REF_CONST = ('REF_CONST', 'nothing', str)
```

## Грамматика языка
```
Program -> (Func)+
Func ->  FuncHeader FuncBody 
FuncHeader -> FuncHeaderShort | 
FuncHeaderLong -> "(" Type "[" FUNCNAME FuncParams "]" ")" 
FuncHeaderShort ->  "[" FUNCNAME FuncParams "]" 
FuncBody -> Statements "%%"
FuncParams -> (BasicVar)*
BasicVar -> "(" Type IDENT ")"
Type -> VAR_TYPE | "<" Type ">"
Statements -> Statement ("," Statement)*
VAR_TYPE -> 'int' | 'bool' | 'char'

Statement -> "^" Expr 
           | "\\" Expr
           | Var ":=" Expr
           | "[" FUNCNAME Args "]"
           | "(" Type IDENT ((")" (":=" Expr)?) | (Cycle Statements "%"))
           |"(" "&" Expr ")" Statements "%"
           | "(" "&" Expr ")" Statements "%"
           |"(" "?" Expr ")" Statements ("+++" Statements)? "%"
           
Cycle -> ":" Expr "," Expr ("," INT_CONST)? ")"
Args -> (Spec)+ 
Expr -> LogicalExpr ((_or_ | _xor_) LogicalExpr)*
LogicalExpr -> CompareExpr (_and_ CompareExpr)*
CompareExpr -> ArithmExpr (CmpOp ArithmExpr)?
CmpOp → _eq_ | _ne_ | _lt_ | _gt_ | _le_ | _ge_
ArithmExpr -> PowExpr (("+" | "-")  PowExpr)*
PowExpr -> Term (_pow_ PowExpr)?
Term -> Factor (("*" | "/" | _mod_) Factor)*
Factor -> (not_ | "-")? Spec
FuncCall -> "[" FUNCNAME Args "]"
Spec -> FuncCall 
      | new_ Type (IDENT | INT_CONST) 
      | INT_CONST | CHAR_CONST | STRING_CONST | REF_CONST | BOOL_CONST 
      | Var 
      | "(" Expr ")"
Var -> IDENT | "<" Spec Expr ">" .

```

## Программная реализация

Файл `Position.py`

```python
import re
import unicodedata

class Position:
    def __init__(self, text, i, l, c):
        self.text = text
        self.line = l
        self.pos = c
        self.index = i

    def __str__(self):
        return f"({self.line}, {self.pos})"

    def Line(self):
        return self.line

    def Pos(self):
        return self.pos

    def Index(self):
        return self.index

    def CompareTo(self, other):
        return self.index - other.index


    def Cp(self):
        return -1 if self.index == len(self.text) else ord(self.text[self.index])

    def Uc(self):
        if self.index == len(self.text):
            return unicodedata.category('\uFFFD')
        else:
            return unicodedata.category(self.text[self.index])

    def IsWhiteSpace(self):
        return self.index != len(self.text) and self.text[self.index].isspace()

    def IsLetter(self):
        return re.match(r'[a-zA-Z]', self.text[self.index])

    def IsDigit(self):
        return self.index != len(self.text) and self.text[self.index].isdigit()

    def IsLetterOrDigit(self):
        return re.match(r'\w', self.text[self.index])

    def IsUnderlining(self):
        return self.text[self.index] == '_'

    def isNewLine(self):
        return self.text[self.index] == '\n'

    def IsCloseBracket(self):
        return self.text[self.index] in [')', ']', '>', ',']

    def Next(self):
        if self.index < len(self.text):
            if self.isNewLine():
                i = self.index
                l = self.line + 1
                return Position(self.text, i + 1, l, 1)
            else:
                i = self.index
                c = self.pos + 1
                return (Position(self.text, i + 1, self.line, c))
        return self

    def SkipErrors(self):
        while not self.IsWhiteSpace():
            pos = Position(self.text, self.line, self.pos, self.index)
            if self.Next() == pos:
                break

    def GetSymbol(self):
        return self.text[self.index]

```

Файл `Fragment.py`
```python
from dataclasses import dataclass

from position import Position


@dataclass
class Fragment:
    starting: Position
    following: Position

    def __str__(self):
        return f"{self.starting}-{self.following}"
```

Файл `Scanner.py`
```python
import tag
from fragment import Fragment
from message import Message
from position import Position
from tok import Token

def sorted_map_keys(m):
    keys = m.keys()
    key_list = sorted(keys, key=lambda k: (k.line, k.pos))
    return key_list

class Compiler:
    def __init__(self):
        self.messages = {}
        self.name_codes = {}
        self.names = []

    def GetScanner(self, program):
        return Scanner(program, self)

    def get_idents_names(self):
        print("IDENTs:")
        for i, name in enumerate(self.names):
            print(f"{i}: {name}")
        print()

    def add_name(self, name):
        name1 = name.lower()
        if name1 in self.name_codes:
            return self.name_codes[name1]
        code = len(self.names)
        self.names.append(name)
        self.name_codes[name1] = code
        return code

    def get_name(self, code):
        return self.names[code]

    def AddMessage(self, is_error, p, text):
        self.messages[p] = Message(is_error, text)

    def output_messages(self):
        key_list = sorted_map_keys(self.messages)
        for key in key_list:
            val = self.messages[key]
            message_type = "Error" if val.is_error else "Warning"
            print(f"{message_type} {str(key)}: {val.text}")
class Comment:
    def __init__(self, starting, following, value):
        self.starting = starting
        self.following = following
        self.value = value

    def __str__(self):
        return f"COMMENT {self.starting}-{self.following}: {self.value}"

class Scanner:
    def __init__(self, program: str, compiler : Compiler):
        self.programReader = program
        self.compiler = compiler
        self.curPos = Position(program, 0, 1, 1)
        self.comments = []

    def printComments(self):
        for comm in self.comments:
            print(comm)

    def NextToken(self):
        curWord = ""
        while self.curPos.Cp() != -1:
            while self.curPos.IsWhiteSpace():
                self.curPos = self.curPos.Next()
            start = self.curPos
            if self.curPos.isNewLine():
                self.curPos = self.curPos.Next()

            elif chr(self.curPos.Cp()) == ':':

                curWord += chr(self.curPos.Cp())
                self.curPos = self.curPos.Next()
                if self.curPos.GetSymbol() == '=':
                    curWord += chr(self.curPos.Cp())
                    pos = self.curPos
                    self.curPos = self.curPos.Next()
                    return Token(tag.DomainTag.SPEC_SYMB, Fragment(start, pos), curWord)

                return Token(tag.DomainTag.SPEC_SYMB, Fragment(start, start), curWord)
            elif chr(self.curPos.Cp()) == '%':
                curWord += chr(self.curPos.Cp())
                self.curPos = self.curPos.Next()
                if chr(self.curPos.Cp()) == '%':
                    curWord += chr(self.curPos.Cp())
                    pos = self.curPos
                    self.curPos = self.curPos.Next()
                    return Token(tag.DomainTag.SPEC_SYMB, Fragment(start, pos), curWord)

                return Token(tag.DomainTag.SPEC_SYMB, Fragment(start, start), curWord)
            elif chr(self.curPos.Cp()) == '"':
                self.curPos = self.curPos.Next()
                # pos = Position()
                if not self.curPos.isNewLine() and self.curPos.Cp() != -1 \
                    and self.curPos.GetSymbol() != '"':
                    curWord += chr(self.curPos.Cp())
                    pos = self.curPos
                    self.curPos = self.curPos.Next()

                    if self.curPos.GetSymbol() == '"':
                        pos = self.curPos
                        self.curPos = self.curPos.Next()
                        return Token(tag.DomainTag.CHAR_CONST, Fragment(start, pos), curWord)
                self.compiler.AddMessage(True, start, "invalid syntax")
                self.curPos.SkipErrors()
                return Token(tag.DomainTag.ERR, Fragment(self.curPos, self.curPos), "")
            elif chr(self.curPos.Cp()) == '\'':
                self.curPos = self.curPos.Next()
                # pos = Position()
                while self.curPos.Cp() != -1 and self.curPos.GetSymbol() != '\''\
                        and not self.curPos.isNewLine():
                    curWord += str(self.curPos.Cp())
                    pos = self.curPos
                    self.curPos = self.curPos.Next()
                if self.curPos.GetSymbol() == '\'':
                    pos = self.curPos
                    self.curPos = self.curPos.Next()
                    return Token(tag.DomainTag.STRING_CONST, Fragment(start, pos), curWord)
                self.compiler.AddMessage(True, start, "invalid syntax")
                self.curPos.SkipErrors()
                return Token(tag.DomainTag.ERR, Fragment(self.curPos, self.curPos), "")
            elif chr(self.curPos.Cp()) == '+':
                curWord += chr(self.curPos.Cp())
                self.curPos = self.curPos.Next()
                pos = self.curPos
                while self.curPos.GetSymbol() == '+':
                    curWord += chr(self.curPos.Cp())
                    pos = self.curPos
                    self.curPos = self.curPos.Next()
                if not self.curPos.isNewLine() and not self.curPos.IsWhiteSpace()\
                        and self.curPos.Cp() != -1:
                    self.compiler.AddMessage(True, start, "invalid syntax")
                    self.curPos.SkipErrors()
                    return Token(tag.DomainTag.ERR, Fragment(self.curPos, self.curPos), "")
                if curWord == "+++" or curWord == "+":
                    return Token(tag.DomainTag.SPEC_SYMB, Fragment(start, pos), curWord)
                self.compiler.AddMessage(True, start, "invalid syntax")
                self.curPos.SkipErrors()
                return Token(tag.DomainTag.ERR, Fragment(self.curPos, self.curPos), "")
            elif self.curPos.Cp() == '{':
                self.curPos = self.curPos.Next()
                while not self.curPos.isNewLine() and self.curPos.Cp() != -1\
                        and self.curPos.GetSymbol() != '}':
                    curWord += chr(self.curPos.Cp())
                    self.curPos = self.curPos.Next()
                self.comments.append(Comment(start, self.curPos, curWord))
                self.curPos = self.curPos.Next()
                curWord = ""
            elif chr(self.curPos.Cp()) in ['_', '!', '@', '.', '#']:
                curWord += chr(self.curPos.Cp())
                self.curPos = self.curPos.Next()
                while self.curPos.IsLetter():
                    curWord += chr(self.curPos.Cp())
                    pos = self.curPos
                    self.curPos = self.curPos.Next()
                if self.curPos.IsUnderlining():
                    curWord += chr(self.curPos.Cp())
                    pos = self.curPos
                    self.curPos = self.curPos.Next()
                    if curWord in tag.keywordsWithUnderliningStart:
                        return Token(tag.DomainTag.KEYWORD, Fragment(start, pos), curWord)
                    self.compiler.AddMessage(True, start, "invalid syntax")
                    self.curPos.SkipErrors()
                    return Token(tag.DomainTag.ERR, Fragment(self.curPos, self.curPos), "")
                if not self.curPos.IsCloseBracket() and not self.curPos.isNewLine()\
                        and not self.curPos.IsWhiteSpace()\
                        and self.curPos.Cp() != -1:
                    self.compiler.AddMessage(True, start, "invalid syntax")
                    self.curPos.SkipErrors()
                    return Token(tag.DomainTag.ERR, Fragment(self.curPos, self.curPos), "")
                return Token(tag.DomainTag.VARNAME, Fragment(start, self.curPos), curWord)
            else:

                if str(self.curPos.GetSymbol()) in tag.specSymbsInOneRune:
                    curWord += chr(self.curPos.Cp())

                    self.curPos =  self.curPos.Next()

                    return Token(tag.DomainTag.SPEC_SYMB, Fragment(start, start), curWord)
                if self.curPos.IsDigit():
                    curWord += chr(self.curPos.Cp())
                    self.curPos = self.curPos.Next()
                    # pos = Position()
                    while self.curPos.IsLetterOrDigit():
                        curWord += chr(self.curPos.Cp())
                        pos = self.curPos
                        self.curPos = self.curPos.Next()
                    if self.curPos.GetSymbol() == '{':
                        curWord += chr(self.curPos.Cp())
                        self.curPos = self.curPos.Next()
                        while self.curPos.IsDigit():
                            curWord += chr(self.curPos.Cp())
                            pos = self.curPos
                            self.curPos = self.curPos.Next()
                        if self.curPos.GetSymbol() != '}' and not self.curPos.IsCloseBracket()\
                                and not self.curPos.isNewLine() and\
                                not self.curPos.IsWhiteSpace() and self.curPos.Cp() != -1:
                            self.compiler.AddMessage(True, start, "invalid syntax")
                            self.curPos.SkipErrors()
                            return Token(tag.DomainTag.ERR, Fragment(self.curPos, self.curPos), "")
                        curWord += chr(self.curPos.Cp())
                        pos = self.curPos
                        self.curPos = self.curPos.Next()
                        return Token(tag.DomainTag.INT_CONST, Fragment(start, pos), curWord)
                    if not self.curPos.IsCloseBracket() and not self.curPos.isNewLine()\
                            and not self.curPos.IsWhiteSpace() and self.curPos.Cp() != -1:
                        self.compiler.AddMessage(True, start, "invalid syntax")
                        self.curPos.SkipErrors()
                        return Token(tag.DomainTag.ERR, Fragment(self.curPos, self.curPos), "")
                    return Token(tag.DomainTag.INT_CONST, Fragment(start, self.curPos), curWord)
                if self.curPos.IsLetter():
                    curWord += chr(self.curPos.Cp())
                    self.curPos = self.curPos.Next()
                    # pos = Position()
                    while self.curPos.IsLetter():
                        curWord += chr(self.curPos.Cp())
                        pos = self.curPos
                        self.curPos = self.curPos.Next()
                    if self.curPos.IsDigit():
                        continue
                    if self.curPos.IsUnderlining():
                        curWord += chr(self.curPos.Cp())
                        pos = self.curPos
                        self.curPos = self.curPos.Next()
                        if curWord in tag.keywords:
                            return Token(tag.DomainTag.KEYWORD, Fragment(start, pos), curWord)
                        self.compiler.AddMessage(True, start, "invalid syntax")
                        self.curPos.SkipErrors()
                        return Token(tag.DomainTag.ERR, Fragment(self.curPos, self.curPos), "")
                    if not self.curPos.IsCloseBracket() and not self.curPos.isNewLine()\
                            and not self.curPos.IsWhiteSpace() and self.curPos.Cp() != -1:
                        self.compiler.AddMessage(True, start, "invalid syntax")
                        self.curPos.SkipErrors()
                        return Token(tag.DomainTag.ERR, Fragment(self.curPos, self.curPos), "")
                    if curWord in tag.keywords:
                        return Token(tag.DomainTag.KEYWORD, Fragment(start, self.curPos), curWord)
                    return Token(tag.DomainTag.FUNCNAME, Fragment(start, self.curPos), curWord)
                self.compiler.AddMessage(True, start, "invalid syntax")
                self.curPos.SkipErrors()
                return Token(tag.DomainTag.ERR, Fragment(self.curPos, self.curPos), "")
        return Token(tag.DomainTag.EOP, Fragment(self.curPos, self.curPos), "")

```

Файл `Node.py`
```python
from dataclasses import dataclass
from abc import ABC, abstractmethod

from tok import Token

mainIdent = "\t"
blockIdent = "  "


@dataclass
class NodePrinter:
    def Print(self, indent):
        pass


class Type(ABC):
    def Print(self, indent):
        pass


@dataclass
class BasicType(Type):
    varType: Token
    def Print(self, indent: str):
        print(f"{indent}BasicType: {str(self.varType.val)}")

@dataclass
class VarType(Type):
    type: Token

    def Print(self, indent):
        print(f"{indent}VarType: {self.type.val}")



@dataclass
class ArrType(Type):
    arrType: VarType

    def Print(self, indent):
        print(indent + "RefType: ", "ArrType")
        return self.arrType.Print(indent + blockIdent)



@dataclass
class BasicVar:
    t: Type
    varname: Token

    def Print(self, indent):
        print(indent + "BasicVar:")
        print(indent + mainIdent + "VarType:")
        self.t.Print(indent + mainIdent + blockIdent)
        print(indent + mainIdent + "VarName: " + str(self.varname))

class Statement(ABC):

    @abstractmethod
    def Print(self, param):
        pass


@dataclass
class Statements(Statement):
    statements: list[Statement]

    def Print(self, indent):
        print(indent + "Statements: ")
        for statement in self.statements:
            statement.Print(indent + mainIdent)


@dataclass
class FuncParams:
    basicVars: list[BasicVar]

    def Print(self, indent):
        print(indent + "FuncParams:")
        for bv in self.basicVars:
            bv.Print(indent + mainIdent)


@dataclass
class FuncHeader:
    t: Type or None or ArrType
    funcName: Token
    params: FuncParams

    def Print(self, indent):
        print(indent + "FuncHeader:")
        if self.t != None:
            print(indent + mainIdent + "FuncType:")
            self.t.Print(indent + mainIdent + blockIdent)
        print(indent + mainIdent + "FuncName: " + str(self.funcName.val))
        self.params.Print(indent + mainIdent)


@dataclass
class FuncBody:
    statements: Statements

    def Print(self, indent):
        print(indent + "FuncBody:")
        self.statements.Print(indent + mainIdent)


@dataclass
class Func:
    header: FuncHeader
    body: FuncBody

    def Print(self, indent):
        print(indent + "Func:")
        self.header.Print(indent + mainIdent)
        self.body.Print(indent + mainIdent)


@dataclass
class Program:
    funcs: list[Func]

    def Print(self, indent):
        print(indent + "Program:")
        for f in self.funcs:
            f.Print(indent + mainIdent)


class Expr(ABC):
    def Print(self, indent):
        pass


@dataclass
class ReturnStatement(Statement):
    expr: Expr

    def Print(self, indent):
        print(indent + "ReturnStatement: ")
        self.expr.Print(indent + mainIdent)


@dataclass
class WarningStatement(Statement):
    expr: Expr

    def Print(self, indent):
        print(indent + "WarningStatement: ")
        self.expr.Print(indent + mainIdent)


@dataclass
class AssignmentStatement(Statement):
    v: Expr
    expr: Expr

    def Print(self, indent):
        print(indent + "AssignmentStatement: ")
        self.v.Print(indent + mainIdent)
        self.expr.Print(indent + mainIdent)


@dataclass
class WhileStatement(Statement):
    expr: Expr
    statements: Statements

    def Print(self, indent):
        print(indent + "WhileStatement: ")
        indent += blockIdent
        print(indent + "WhileCondition: ")
        self.expr.Print(indent + mainIdent)
        print(indent + "WhileBody: ")
        self.statements.Print(indent + mainIdent)


@dataclass
class IfStatement(Statement):
    expr: Expr
    thenBranch: Statements
    elseBranch: Statements

    def Print(self, indent=""):
        print(indent + "IfStatement: ")
        print(indent + "\tIfCondition: ")
        self.expr.Print(indent + "\t\t")
        print(indent + "\tThenBranchBody: ")
        self.expr.Print(indent + "\t\t")
        if self.elseBranch is not None:
            print(indent + "\tElseBranchBody: ")
            self.elseBranch.Print(indent + "\t\t")


@dataclass
class VarDeclarationStatement(Statement):
    t: Type
    varname: Token

    def Print(self, indent=""):
        print(indent + "VarDeclarationStatement:")
        print(indent + "\tVarType: ")
        self.t.Print(indent + "\t\t")
        print(indent + "\tVarName: " + str(self.varname.val))


@dataclass
class ForStatement(Statement):
    t: Type
    varname: Token
    start: Expr
    end: Expr
    step: Token
    statements: Statements

    def Print(self, indent=""):
        print(indent + "ForStatement: ")
        print(indent + "\tForHeader: ")
        print(indent + "\t\tVarType: ")
        self.t.Print(indent + "\t\t\t")
        print(indent + "\t\tVarName: " + str(self.varname.val))

        print(indent + "\t\tForStart: ")
        self.start.Print(indent + "\t\t\t")
        print(indent + "\t\tForEnd: ")
        self.end.Print(indent + "\t\t\t")
        if self.step is not None:
            print(indent + "\t\tForStep: " + str(self.step.val))


@dataclass
class Cycle:
    start: Expr
    end: Expr
    step: Token

    def Print(self, indent=""):
        print(indent + "Cycle: ")
        print(indent + "\tStart: ")
        self.start.Print(indent + "\t\t")
        print(indent + "\tEnd: ")
        self.end.Print(indent + "\t\t")
        if self.step is not None:
            print(indent + "\tStep: " + str(self.step.val))


@dataclass
class ConstExpr(Expr):
    t: Type or None
    val: Token

    def Print(self, indent=""):
        print(indent + "ConstExpr: ")
        if self.t is not None:
            self.t.Print(indent + "\t")
        print(indent + "\tVal: " + str(self.val.val))


@dataclass
class BinOpExpr(Expr):
    left: Expr
    op: Token
    right: Expr

    def Print(self, indent=""):
        print(indent + "BinOpExpr: ")
        self.left.Print(indent + "\t")
        print(indent + "\tOp: " + str(self.op.val))
        self.right.Print(indent + "\t")


@dataclass
class UnOpExpr(Expr):
    op: Token
    expr: Expr

    def Print(self, indent=""):
        print(indent + "BinOpExpr: ")
        print(indent + "\tOp: " + str(self.op.val))
        self.expr.Print(indent + "\t")


@dataclass
class VarExpr(Expr):
    varName: Token or None
    array: Expr or None
    index: Expr or None

    def Print(self, indent=""):
        print(indent + "VarExpr: ")
        if self.array is not None:

            print(indent + "\tArrayElemByIndex " )
            self.array.Print(indent + "\t\t")
            self.index.Print(indent + "\t\t")
        else:
            print(indent + "\tVarExprName: " + str(self.varName.val))


@dataclass
class AllocExpr(Expr):
    t: Type
    size: Token

    def Print(self, indent=""):
        print(indent + "AllocExpr: ")
        self.t.Print(indent + "\t")
        print(indent + "\tSize: " + self.size.val)


@dataclass
class FuncCall:
    funcName: Token
    args: list[Expr]

    def Print(self, indent=""):
        print(indent + "FuncCall: ")
        print(indent + "\tFuncName: " + str(self.funcName.val))
        print(indent + "\tArgs: ")
        for arg in self.args:
            arg.Print(indent + "\t\t")


```

Файл `Tag.py`
```python

from enum import Enum
class DomainTag(Enum):
    VARNAME = 0
    FUNCNAME = 1
    INT_CONST = 2
    CHAR_CONST = 3
    STRING_CONST = 4
    KEYWORD = 5
    SPEC_SYMB = 6
    ERR = 7
    EOP = 8


tagToString = {
    DomainTag.VARNAME: "VARNAME",
    DomainTag.FUNCNAME: "FUNCNAME",
    DomainTag.INT_CONST: "INT_CONST",
    DomainTag.CHAR_CONST: "CHAR_CONST",
    DomainTag.STRING_CONST: "STRING_CONST",
    DomainTag.KEYWORD: "KEYWORD",
    DomainTag.SPEC_SYMB: "SPEC_SYMB",
    DomainTag.EOP: "EOP",
    DomainTag.ERR: "ERR"
}

keywords = {
    "bool",
    "char",
    "int",
    "false",
    "true",
    "nothing",
    "new_",
    "not_"
}

keywordsWithUnderliningStart = {
    "_and_",
    "_eq_",
    "_ge_",
    "_gt_",
    "_le_",
    "_lt_",
    "_mod_",
    "_ne_",
    "_or_",
    "_pow_",
    "_xor_"
}

specSymbsInOneRune = {
    "<",
    ">",
    "(",
    ")",
    "[",
    "]",
    ",",
    "?",
    "&",
    "\\",
    "^",
    "-",
    "*",
    "/"
}

```

Файл `Tok.py`
```python
from fragment import Fragment
from dataclasses import dataclass
from tag import DomainTag, tagToString

@dataclass
class Token:
    tag: DomainTag or None
    coord : Fragment or None
    val: str or None

    def __str__(self):
        return f"{tagToString[self.tag]} {str(self.coord.starting)\
            , str(self.coord.following)} : {self.val}"

    def Tag(self):
        return self.tag
```

Файл `Parser.py`
```python
import tag
from node import Program, FuncHeader, Func, FuncParams, BasicVar,\
    Statements, ReturnStatement, WarningStatement, \
    FuncCall, AssignmentStatement, VarDeclarationStatement,\
    ForStatement, IfStatement, WhileStatement, Cycle, BinOpExpr, \
    AllocExpr, ConstExpr, FuncBody, ArrType, VarType, VarExpr
from scanner import Scanner



class Parser:
    def __init__(self, scanner: Scanner):
        self.sym = scanner.NextToken()
        self.scanner = scanner


    def ExpectTags(self, *tags):
        for tag in tags:
            if self.sym.tag == tag:
                sym = self.sym
                self.sym = self.scanner.NextToken()
                if self.sym.tag == "ERR":
                    raise Exception("parse error: unexpected token")
                return sym

        raise Exception("parse error: expected {}, but got {}".format(tags, self.sym))

    # Program -> (Func) +
    def program(self):
        funcs = []
        funcs.append(self.Func())
        while self.sym.val == "[" or self.sym.val == "(":
            funcs.append(self.Func())

        return Program(funcs)


    def ExpectStr(self, *vals):
        for val in vals:

            if self.sym.val == val:
                sym = self.sym

                self.sym = self.scanner.NextToken()

                if self.sym.tag == tag.DomainTag.ERR:
                    raise Exception("parse error: unexpected token")
                return sym

        raise Exception(f"parse error: expected {vals}, but got\
         {self.sym.val}, {str(self.sym.coord)}")

#  Func ->  FuncHeader FuncBody
    def Func(self):
        header = self.FuncHeader()
        body = self.FuncBody()

        return Func(header, body)

    # Type -> '<' Type '>' | 'int' | 'bool' | 'char'
    def Type(self):
        if self.sym.val == "<":
            self.ExpectStr("<")
            t = self.Type()
            self.ExpectStr(">")
            return ArrType(t)
        varT = self.ExpectStr("int", "bool", "char")
        return VarType(varT)


    #FuncHeader -> "(" Type "[" FUNCNAME FuncParams "]" ")"
    #FuncHeader -> "[" FUNCNAME FuncParams "]"
    def FuncHeader(self):
        if self.sym.val == "(":
            self.ExpectStr("(")
            t = self.Type()

            self.ExpectStr("[")
            funcName = self.ExpectTags(tag.DomainTag.FUNCNAME)
            params = self.FuncParams()
            self.ExpectStr("]")
            self.ExpectStr(")")
            return FuncHeader(t, funcName, params)

        self.ExpectStr("[")
        funcName = self.ExpectTags(tag.DomainTag.FUNCNAME)
        params = self.FuncParams()
        self.ExpectStr("]")
        return FuncHeader(None, funcName, params)

# FuncBody -> Statements "%%"
    def FuncBody(self):
        statements = self.Statements()
        self.ExpectStr("%%")
        return FuncBody(statements)


#FuncParams -> (BasicVar)*
    def FuncParams(self):
        basicVars = []
        while self.sym.val == "(":
            basicVars.append(self.BasicVar())

        return FuncParams(basicVars)


#BasicVar -> "(" Type VARNAME ")"
    def BasicVar(self):
        self.ExpectStr("(")
        t = self.Type()
        varname = self.ExpectTags(tag.DomainTag.VARNAME)
        self.ExpectStr(")")

        return BasicVar(t, varname)


#Statements -> Statement ("," Statement)*
    def Statements(self):
        statement = []
        statement.append(self.Statement())
        while self.sym.val == ",":
            self.ExpectStr(",")
            statement.append(self.Statement())

        return Statements(statement)


    #   Statement -> "^" Expr
    #   Statement -> "\\" Expr
    #   Statement -> Var ":=" Expr
    #   Statement -> "[" FUNCNAME Args "]"
    #   Statement -> "(" StatementTail
    def Statement(self):
        if self.sym.val == "^":
            self.ExpectStr("^")
            expr = self.Expr()
            return ReturnStatement(expr)
        elif self.sym.val == "\\":
            self.ExpectStr("\\")
            expr = self.Expr()
            return WarningStatement(expr)
        elif self.sym.val == "[":
            self.ExpectStr("[")
            funcName = self.ExpectTags(tag.DomainTag.FUNCNAME)
            args = self.Args()
            self.ExpectStr("]")
            return FuncCall(funcName, args)
        elif self.sym.tag == tag.DomainTag.VARNAME or self.sym.val == "<":
            v = self.Var()
            self.ExpectStr(":=")
            expr = self.Expr()
            return AssignmentStatement(v, expr)
        else:
            self.ExpectStr("(")
            return self.StatementTail()


    #  StatementTail -> Type VARNAME ((")" (":=" Expr)?) | (Cycle Statements "%"))
    #  StatementTail -> "&" Expr ")" Statements "%"
    #  StatementTail -> "?" Expr ")" Statements ("+++" Statements)? "%"
    def StatementTail(self):
        if self.sym.val == "<" or self.sym.val == "int"\
                or self.sym.val == "bool" or self.sym.val == "char":
            t = self.Type()
            varname = self.ExpectTags(tag.DomainTag.VARNAME)
            if self.sym.val == ")":
                self.ExpectStr(")")
                if self.sym.val == ":=":
                    self.ExpectStr(":=")
                    expr = self.Expr()
                    return AssignmentStatement(ConstExpr(t, varname), expr)
                return VarDeclarationStatement(t, varname)
            elif self.sym.val == ":":
                cycle = self.Cycle()
                statements = self.Statements()
                self.ExpectStr("%")
                return ForStatement(t, varname, cycle.start,\
                                    cycle.end, cycle.step, statements)
            else:
                raise Exception("parse error")
        elif self.sym.val == "?":
            self.ExpectStr("?")
            expr = self.Expr()
            self.ExpectStr(")")
            thenBranch = self.Statements()
            elseBranch = None
            if self.sym.val == "+++":
                self.ExpectStr("+++")
                elseBranch_ = self.Statements()
                elseBranch = elseBranch_
            self.ExpectStr("%")
            return IfStatement(expr, thenBranch, elseBranch)
        else:
            self.ExpectStr("&")
            expr = self.Expr()
            self.ExpectStr(")")
            statements = self.Statements()
            self.ExpectStr("%")
            return WhileStatement(expr, statements)

    # Cycle -> VARNAME ":" Expr "," Expr ("," INT_CONST)? ")"

    def Cycle(self):
        self.ExpectStr(":")
        startExpr = self.Expr()
        self.ExpectStr(",")
        endExpr = self.Expr()
        step = None
        if self.sym.val == ",":
            self.ExpectStr(",")
            token_ = self.ExpectTags(tag.DomainTag.INT_CONST)
            step = token_
        self.ExpectStr(")")

        return Cycle(startExpr, endExpr, step)

    #Args -> (Spec)+

    def Args(self):
        specs = []
        specs.append(self.Spec())
        while self.sym.val == "(" or self.sym.val == "[" or self.sym.val == "<"\
                or self.sym.val == "new_" \
                or self.sym.val == "true" or self.sym.val == "false"\
                or self.sym.tag == tag.DomainTag.INT_CONST\
                or self.sym.tag == tag.DomainTag.CHAR_CONST\
                or self.sym.tag == tag.DomainTag.STRING_CONST\
                or self.sym.tag == tag.DomainTag.VARNAME:
            specs.append(self.Spec())

        return specs

    # Expr -> LogicalExpr ((_or_ | _xor_) LogicalExpr)*

    def Expr(self):
        expr = self.LogicalExpr()
        while self.sym.val == "_or_" or self.sym.val == "_xor_":
            op = self.ExpectStr("_or_", "_xor_")
            rightExpr = self.LogicalExpr()
            expr = BinOpExpr(expr, op, rightExpr)

        return expr

    # LogicalExpr -> CompareExpr (_and_ CompareExpr)*
    def LogicalExpr(self):
        expr = self.CompareExpr()
        while self.sym.val == "_and_":
            op = self.ExpectStr("_and_")
            rightExpr = self.CompareExpr()
            expr = BinOpExpr(expr, op, rightExpr)

        return expr


    #CompareExpr -> ArithmExpr (CmpOp ArithmExpr)*
    def CompareExpr(self):
        expr = self.ArithmExpr()
        if self.sym.val == "_eq_" or self.sym.val == "_ne_" or self.sym.val == "_lt_"\
                or self.sym.val == "_gt_" or self.sym.val == "_le_" or self.sym.val == "_ge_":
            op = self.CmpOp()
            rightExpr = self.ArithmExpr()

            expr = BinOpExpr(expr, op, rightExpr)

        return expr

    def CmpOp(self):
        return self.ExpectStr("_eq_", "_ne_", "_lt_", "_gt_", "_le_", "_ge_")


    # ArithmExpr -> PowExpr (("+" | "-")  PowExpr)*
    def ArithmExpr(self):
        expr = self.PowExpr()
        while self.sym.val == "+" or self.sym.val == "-":
            op = self.ExpectStr("+", "-")
            rightExpr = self.PowExpr()

            expr = BinOpExpr(expr, op, rightExpr)

        return expr


    #PowExpr -> Term (_pow_ PowExpr)?
    def PowExpr(self):
        expr = self.Term()
        if self.sym.val == "_pow_":
            op = self.ExpectStr("_pow_")
            rightExpr = self.PowExpr()
            expr = BinOpExpr(expr, op, rightExpr)

        return expr


    # Term -> Factor (("*" | "/" | _mod_) Factor)*
    def Term(self):
        expr = self.Factor()
        while self.sym.val == "*" or self.sym.val == "/" or self.sym.val == "_mod_":
            op = self.ExpectStr("*", "/", "_mod_")
            rightExpr = self.Factor()
            return BinOpExpr(expr, op, rightExpr)

        return expr


    #  Factor -> (not_ | "-")? Spec

    def Factor(self):
        if self.sym.val == "not_":
            self.ExpectStr("not_")
        elif self.sym.val == "-":
            self.ExpectStr("-")

        return self.Spec()


    #FuncCall -> "[" FUNCNAME Args "]"

    def FuncCall(self):
        self.ExpectStr("[")
        funcname = self.ExpectTags(tag.DomainTag.FUNCNAME)
        args = self.Args()
        self.ExpectStr("]")

        return FuncCall(funcname, args)

    # Spec -> FuncCall
    # Spec -> new_ Type(VARNAME | INT_CONST)
    # Spec -> Const
    # Spec -> Var
    # Spec -> "("Expr")"
    def Spec(self):
        if self.sym.val == "(":
            self.ExpectStr("(")
            expr = self.Expr()
            self.ExpectStr(")")
            return expr
        elif self.sym.val == "<" or self.sym.tag == tag.DomainTag.VARNAME:
            varExpr = self.Var()
            return varExpr
        elif self.sym.val == "true" or self.sym.val == "false" or self.sym.val == "nothing"\
                or self.sym.tag == tag.DomainTag.INT_CONST\
                or self.sym.tag == tag.DomainTag.CHAR_CONST\
                or self.sym.tag == tag.DomainTag.STRING_CONST:
            return self.Const()
        elif self.sym.val == "[":
            return self.FuncCall()
        else:
            self.ExpectStr("new_")
            t = self.Type()
            size = self.ExpectTags(tag.DomainTag.VARNAME, tag.DomainTag.INT_CONST)
            return AllocExpr(t, size)


    #Var -> VARNAME | "<" Spec Expr ">"
    def Var(self):
        if self.sym.val == "<":
            self.ExpectStr("<")
            arrayName = self.Spec()
            expr = self.Expr()
            self.ExpectStr(">")
            return VarExpr(None, arrayName, expr)

        varname = self.ExpectTags(tag.DomainTag.VARNAME)
        return VarExpr(varname, None, None)

    #Const → INT_CONST | CHAR_CONST | STRING_CONST | REF_CONST | BOOL_CONST

    def Const(self):
        if self.sym.tag == tag.DomainTag.INT_CONST or self.sym.tag == tag.DomainTag.CHAR_CONST\
                or self.sym.tag == tag.DomainTag.STRING_CONST:
            val = self.ExpectTags(tag.DomainTag.INT_CONST,\
                                  tag.DomainTag.CHAR_CONST, tag.DomainTag.STRING_CONST)
            return ConstExpr(None, val)
        str = self.ExpectStr("true", "false", "nothing")
        return ConstExpr(None, str)

```

Файл `Main.py`
```python
from parser import Parser
from scanner import Compiler


def main():

    filePath = "/Users/assistentka_professora/Desktop/Compile/lab2_4/in.txt"
    with open(filePath, 'r') as file:
        reader = file.read()

    compiler = Compiler()

    scn = compiler.GetScanner(reader)
    parser = Parser(scn)

    p = parser.program()
    p.Print("")

if __name__ == "__main__":
    main()

```


# Тестирование

Входные данные

```
(<int> [SumVectors (<int> !A)
    (<int> !B)]
    )
    (int #size) := [length !A],
    (<int> #C) := new_ <int> 777777F{16},
    !x := !a _eq_ 1,
    #x := #a _pow_ 2,
    <!A 5> := <#B 6> * 10,
    [Factorial #x],
    (<int> #P) := new_ <int> 10,
    (<int> #i : 0, #size - 1)
        <#C #i> := <!A #i> + <!B #i>
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
  _n := _n * [Factorial _n],
  ^ #C
%%


(<int> [Main (<<char>> !args)])
   (<int> !A),
   (<int> !B),
   [SumVectors (!A) (!B)],
   (int @a) := 2,
    ^ #C
%%
```

Вывод на `stdout`

```
Program:
	Func:
		FuncHeader:
			FuncType:
			  RefType:  ArrType
			    VarType: int
			FuncName: SumVectors
			FuncParams:
				BasicVar:
					VarType:
					  RefType:  ArrType
					    VarType: int
					VarName: VARNAME ('(1, 27)', '(1, 29)') : !A
				BasicVar:
					VarType:
					  RefType:  ArrType
					    VarType: int
					VarName: VARNAME ('(2, 12)', '(2, 14)') : !B
		FuncBody:
			Statements: 
				AssignmentStatement: 
					ConstExpr: 
						VarType: int
						Val: #size
					FuncCall: 
						FuncName: length
						Args: 
							VarExpr: 
								VarExprName: !A
				AssignmentStatement: 
					ConstExpr: 
						RefType:  ArrType
						  VarType: int
						Val: #C
					AllocExpr: 
						RefType:  ArrType
						  VarType: int
						Size: 777777F{16}
				AssignmentStatement: 
					VarExpr: 
						VarExprName: !x
					BinOpExpr: 
						VarExpr: 
							VarExprName: !a
						Op: _eq_
						ConstExpr: 
							Val: 1
				AssignmentStatement: 
					VarExpr: 
						VarExprName: #x
					BinOpExpr: 
						VarExpr: 
							VarExprName: #a
						Op: _pow_
						ConstExpr: 
							Val: 2
				AssignmentStatement: 
					VarExpr: 
						ArrayElemByIndex 
							VarExpr: 
								VarExprName: !A
							ConstExpr: 
								Val: 5
					BinOpExpr: 
						VarExpr: 
							ArrayElemByIndex 
								VarExpr: 
									VarExprName: #B
								ConstExpr: 
									Val: 6
						Op: *
						ConstExpr: 
							Val: 10
				FuncCall: 
					FuncName: Factorial
					Args: 
						VarExpr: 
							VarExprName: #x
				AssignmentStatement: 
					ConstExpr: 
						RefType:  ArrType
						  VarType: int
						Val: #P
					AllocExpr: 
						RefType:  ArrType
						  VarType: int
						Size: 10
				ForStatement: 
					ForHeader: 
						VarType: 
							RefType:  ArrType
							  VarType: int
						VarName: #i
						ForStart: 
							ConstExpr: 
								Val: 0
						ForEnd: 
							BinOpExpr: 
								VarExpr: 
									VarExprName: #size
								Op: -
								ConstExpr: 
									Val: 1
				IfStatement: 
					IfCondition: 
						BinOpExpr: 
							VarExpr: 
								VarExprName: #a
							Op: _lt_
							ConstExpr: 
								Val: 0
					ThenBranchBody: 
						BinOpExpr: 
							VarExpr: 
								VarExprName: #a
							Op: _lt_
							ConstExpr: 
								Val: 0
					ElseBranchBody: 
						Statements: 
							IfStatement: 
								IfCondition: 
									BinOpExpr: 
										VarExpr: 
											VarExprName: #a
										Op: _eq_
										ConstExpr: 
											Val: 0
								ThenBranchBody: 
									BinOpExpr: 
										VarExpr: 
											VarExprName: #a
										Op: _eq_
										ConstExpr: 
											Val: 0
								ElseBranchBody: 
									Statements: 
										AssignmentStatement: 
											VarExpr: 
												VarExprName: #sign
											ConstExpr: 
												Val: 1
				ReturnStatement: 
					VarExpr: 
						VarExprName: #C
	Func:
		FuncHeader:
			FuncType:
			  VarType: int
			FuncName: Factorial
			FuncParams:
				BasicVar:
					VarType:
					  VarType: int
					VarName: VARNAME ('(26, 22)', '(26, 24)') : _n
		FuncBody:
			Statements: 
				AssignmentStatement: 
					VarExpr: 
						VarExprName: _n
					BinOpExpr: 
						VarExpr: 
							VarExprName: _n
						Op: *
						FuncCall: 
							FuncName: Factorial
							Args: 
								VarExpr: 
									VarExprName: _n
				ReturnStatement: 
					VarExpr: 
						VarExprName: #C
	Func:
		FuncHeader:
			FuncType:
			  RefType:  ArrType
			    VarType: int
			FuncName: Main
			FuncParams:
				BasicVar:
					VarType:
					  RefType:  ArrType
					    RefType:  ArrType
					      VarType: char
					VarName: VARNAME ('(32, 24)', '(32, 29)') : !args
		FuncBody:
			Statements: 
				VarDeclarationStatement:
					VarType: 
						RefType:  ArrType
						  VarType: int
					VarName: !A
				VarDeclarationStatement:
					VarType: 
						RefType:  ArrType
						  VarType: int
					VarName: !B
				FuncCall: 
					FuncName: SumVectors
					Args: 
						VarExpr: 
							VarExprName: !A
						VarExpr: 
							VarExprName: !B
				AssignmentStatement: 
					ConstExpr: 
						VarType: int
						Val: @a
					ConstExpr: 
						Val: 2
				ReturnStatement: 
					VarExpr: 
						VarExprName: #C
```

# Вывод

В результате выполнения лабораторной работы был разработан парсер, который успешно анализирует
текст на входном языке L4 и строит для него абстрактное синтаксическое дерево.
Парсер также выдает  сообщения об ошибках, включающие координаты сообщения об ошибках.

Метод рекурсивного спуска является эффективным инструментом для построения парсеров для языков.
Он позволяет получить достаточно быстро работающий анализатор. Однако, метод рекурсивного спуска
не может обрабатывать левую рекурсию, поэтому пришлось дополнительно переделать грамматику,
реализованную в ЛР 2_2 -  переписать грамматику, удалив левую рекурсию. 
Но также стоит отметить, реализация этого метода позволила пошагово анализировать текст,
что сделала отладку проще и легче было искать ошибки и несоответствия в парвилах. Еще одним плюсом
можно назвать  хорошо структурированный и легко читаемый код парсера, при необходимости всегда 
можно было легко добавить новые правила грамматики или изменить существующие без 
необходимости изменения всего анализатора.

