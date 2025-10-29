% Лабораторная работа № 2.3 «Синтаксический анализатор на основе
  предсказывающего анализа»
% 18 июня 2024 г.
% Ольга Александрова, ИУ9-61Б

# Цель работы
Целью данной работы является изучение алгоритма построения таблиц предсказывающего анализатора.

# Индивидуальный вариант

```
# ключевые слова
# начинаются с кавычки

F  -> "n" 'or "(" E ")" 'end
T  -> F T1 'end
T1 -> "*" F T1 'or 'epsilon 'end
'axiom E  -> T E1 'end
E1 -> "+" T E1 'or 'epsilon 'end
```

# Реализация

## Неформальное описание синтаксиса входного языка

Программа на входном языке представляет собой набор определений правил

```Program ::= Rule*```

```Rule``` состоит из правой и  левой части, между которыми стоит знак `->`

```
Rule ::= RuleL -> RuleR
```

Левая часть правила является нетерминалом NTERM. Если левая часть — аксиома грамматики,
то нетерминал - ключевое словом AXIOM.

```
RuleL ::= KW_AXIOM |  NTERM
```

Правая часть правила содержит выражение Expr и оканчивается ключевым словом KEY_END.

```
RuleRHS ::= Expr KW_END
```

Expr состоит переменных, которые могут быть записаны через альтернативу KEY_OR.

```
Expr ::= Var+ (KW_OR Var+)*
```

Переменная может являться терминалом TERM, нетерминалом NTERM или быть эпсилон EPS.
```
Var ::= TERM | NTERM | EPS
```

## Лексическая структура
```
WHITESPACE = [ \t\n\r]+
NTERM = [a-zA-Z][a-zA-Z0-9]*
TERM    = \"[^\n"]+\"
OP_ARROW   = ->
AXIOM   = 'axiom
EPS  = 'epsilon
KEY_OR   = 'or
KEY_END  = 'end
```

## Грамматика языка

```
Program -> Rules .
Rules -> Rule Rules | .
Rule -> RuleL OP_ARROW RuleR .
RuleL -> AXIOM NTERM | NTERM .
RuleR -> Expr KEY_END .
Expr -> Term Expr1 .
Expr1 -> KEY_OR Term Expr1 | .
Term -> Var Term1 | EPS .
Term1 -> Var Term1 | .
Var -> TERM | NTERM .
```

## Parsing Table

|  | AXIOM | NTERM | KEY_END | KEY_OR | TERM | $ |
|---|---|---|---|---|---|---|
| Program | Program → Rules | Program → Rules |  |  |  | Program → Rules |
| Rules | Rules → Rule Rules | Rules → Rule Rules |  |  |  | Rules → ε |
| Rule | Rule → RuleL OP_ARROW RuleR | Rule → RuleL OP_ARROW RuleR |  |  |  |  |
| RuleL | RuleL → AXIOM NTERM | RuleL → NTERM |  |  |  |  |
| RuleR |  | RuleR → Expr KEY_END | RuleR → Expr KEY_END | RuleR → Expr KEY_END | RuleR → Expr KEY_END |  |
| Expr |  | Expr → Term Expr1 | Expr → Term Expr1 | Expr → Term Expr1 | Expr → Term Expr1 |  |
| Expr1 |  |  | Expr1 → ε | Expr1 → KEY_OR Term Expr1 |  |  |
| Term |  | Term → Var Term1 | Term → ε | Term → ε | Term → Var Term1 |  |
| Term1 |  | Term1 → Var Term1 | Term1 → ε | Term1 → ε | Term1 → Var Term1 |  |
| Var |  | Var → NTERM |  |  | Var → TERM |  |
## Программная реализация

Файл `Position.py`

```python
import re
import unicodedata

class Fragment:
    def __init__(self, starting, following):
        self.Starting = starting
        self.Following = following

    def __str__(self):
        return str(self.Starting) + "-" + str(self.Following)


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

    def isNewLine(self):
        return self.index != len(self.text) and self.text[self.index] == '\n'

    def IsArrow(self):
        return self.text[self.index] == '->'

    def IsTerminal(self):
        str = self.text[self.index]
        pattern = r"^[a-z]$"
        match = re.match(pattern, str)
        return bool(match)

    def IsNTerminal(self):
        str = self.text[self.index]
        return str.isalpha()
    def IsDigit(self):
        return self.index != len(self.text) and self.text[self.index].isdigit()

    def IsLetterOrDigit(self):
        return re.match(r'\w', self.text[self.index])

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

    def Cp(self):
        return -1 if self.index == len(self.text) else ord(self.text[self.index])

    def Uc(self):
        if self.index == len(self.text):
            return unicodedata.category('\uFFFD')
        else:
            return unicodedata.category(self.text[self.index])

    def IsWhiteSpace(self):
        return self.index != len(self.text) and self.text[self.index].isspace()


```

Файл `Scanner.py`

```python
import position
from position import Position
from collections import OrderedDict, defaultdict
from src.tok import Token, DomainTag


class Message:
    def __init__(self, endPosition, message):
        self.endPosition = endPosition
        self.message = message
    def __str__(self):
        return "ERROR {}: {}".format(self.endPosition, self.message)


class Compiler:
    def __init__(self):
        self.messages = OrderedDict()
        self.nameCodes = defaultdict(int)
        self.names = []

    def AddMessage(self, isErr, c, text):
        self.messages[c] = (isErr, text)

    def OutputMessages(self):
        for pos, (isErr, text) in self.messages.items():
            error_type = "Error" if isErr else "Warning"
            print(f"{error_type} {pos}: {text}")

    def GetScanner(self, program):
        return Scanner(program, self)

    def AddName(self, name):
        if name in self.nameCodes:
            return self.nameCodes[name]
        else:
            code = len(self.names)
            self.names.append(name)
            self.nameCodes[name] = code
            return code

    def GetName(self, code):
        return self.names[code]


class Scanner:
    def __init__(self, program: str, compiler: Compiler):
        self.programReader = program
        self.compiler = compiler
        self.curPos = Position(program, 0, 1, 1)
        self.comments = []

    def NextToken(self):
        curWord = ""
        while self.curPos.Cp() != -1:
            while self.curPos.IsWhiteSpace():
                self.curPos = self.curPos.Next()
            start = self.curPos
            if self.curPos.isNewLine():
                self.curPos = self.curPos.Next()
            if self.curPos.Cp() == -1:
                return Token(DomainTag.END_OF_PROGRAM, position.Fragment(start, start), "")
            elif chr(self.curPos.Cp()) == '-':
                curWord += chr(self.curPos.Cp())
                self.curPos = self.curPos.Next()
                if chr(self.curPos.Cp()) == '>':
                    curWord += chr(self.curPos.Cp())
                    pos = self.curPos
                    self.curPos = self.curPos.Next()
                    return Token(DomainTag.OP_ARROW, position.Fragment(start, pos), curWord)

            elif chr(self.curPos.Cp()) == '"':
                curWord += chr(self.curPos.Cp())
                self.curPos = self.curPos.Next()
                while chr(self.curPos.Cp()) != '"':
                    curWord += chr(self.curPos.Cp())
                    pos = self.curPos
                    self.curPos = self.curPos.Next()
                    return Token(DomainTag.TERM, position.Fragment(start, pos), curWord)

            elif chr(self.curPos.Cp()) == "'":
                curWord += chr(self.curPos.Cp())
                self.curPos = self.curPos.Next()
                while not (self.curPos.IsWhiteSpace()):
                    try:
                        curWord += chr(self.curPos.Cp())
                    except ValueError as e:
                        raise e
                    self.curPos = self.curPos.Next()
                if curWord == "'end":
                    return Token(DomainTag.KEY_END, position.Fragment(start, self.curPos), curWord)
                if curWord == "'or":
                    return Token(DomainTag.KEY_OR, position.Fragment(start, self.curPos), curWord)
                if curWord == "'axiom":
                    return Token(DomainTag.AXIOM, position.Fragment(start, self.curPos), curWord)
                if curWord == "'epsilon":
                    return Token(DomainTag.EPS, position.Fragment(start, self.curPos), curWord)
            elif self.curPos.IsNTerminal() and chr(self.curPos.Cp()) != '-':
                curWord += chr(self.curPos.Cp())
                self.curPos = self.curPos.Next()
                pos = self.curPos
                while self.curPos.IsLetterOrDigit():
                    curWord += chr(self.curPos.Cp())
                    pos = self.curPos
                    self.curPos = self.curPos.Next()

                return Token(DomainTag.NTERM, position.Fragment(start, pos), curWord)

            return Token(DomainTag.ERROR, position.Fragment(self.curPos, self.curPos), "")

        return Token(DomainTag.END_OF_PROGRAM, position.Fragment(self.curPos, self.curPos), "")

```

Файл `Tok.py`

```python
import enum
from dataclasses import dataclass

from src.position import Fragment


class DomainTag(enum.Enum):
    AXIOM = "AXIOM"
    EPS = "EPS"
    KEY_OR = "KEY_OR"
    TERM = "TERM"
    NTERM = "NTERM"
    OP_ARROW = "OP_ARROW"
    KEY_END = "KEY_END"
    END_OF_PROGRAM = "END_OF_PROGRAM"
    ERROR = "ERROR"

    def __str__(self):
        return self.value


@dataclass
class Token:
    tag: DomainTag
    coords : Fragment
    val: str

    def __str__(self):
        return f"{self.tag} {str(self.coords.Starting), str(self.coords.Following)} : {self.val}"



```

Файл `Tok.py`

```python
import enum
from dataclasses import dataclass

from src.position import Fragment


class DomainTag(enum.Enum):
    AXIOM = "AXIOM"
    EPS = "EPS"
    KEY_OR = "KEY_OR"
    TERM = "TERM"
    NTERM = "NTERM"
    OP_ARROW = "OP_ARROW"
    KEY_END = "KEY_END"
    END_OF_PROGRAM = "END_OF_PROGRAM"
    ERROR = "ERROR"

    def __str__(self):
        return self.value


@dataclass
class Token:
    tag: DomainTag
    coords : Fragment
    val: str

    def __str__(self):
        return f"{self.tag} {str(self.coords.Starting), str(self.coords.Following)} : {self.val}"



```
Файл `Parser.py`

```python
from node import Node, NonTerminal, LeafNode, InnerNode
from src.tok import DomainTag, Token
from scanner import Scanner


class AnalyzerTable:
  def __init__(self):
    self.states = [
      [NonTerminal.kRules],  # 0
      [NonTerminal.kRule, NonTerminal.kRules],  # 1
      [],  # 2
      [NonTerminal.kRuleLHS, DomainTag.OP_ARROW, NonTerminal.kRuleR],  # 3
      [DomainTag.AXIOM, DomainTag.NTERM],  # 4
      [DomainTag.NTERM],  # 5
      [NonTerminal.kExpr, DomainTag.KEY_END],  # 6
      [NonTerminal.kTerm, NonTerminal.kExpr1],  # 7
      [DomainTag.KEY_OR, NonTerminal.kTerm, NonTerminal.kExpr1],  # 8
      [NonTerminal.Var, NonTerminal.kTerm1],  # 9
      [DomainTag.TERM],  # 10
      [DomainTag.EPS],  # 11
    ]
    self.tableSt = {
      (NonTerminal.kProgram, DomainTag.NTERM): self.states[0],
      (NonTerminal.kProgram, DomainTag.AXIOM): self.states[0],
      (NonTerminal.kProgram, DomainTag.END_OF_PROGRAM): self.states[0],
      (NonTerminal.kRules, DomainTag.NTERM): self.states[1],
      (NonTerminal.kRules, DomainTag.AXIOM): self.states[1],
      (NonTerminal.kRules, DomainTag.END_OF_PROGRAM): self.states[2],
      (NonTerminal.kRule, DomainTag.NTERM): self.states[3],
      (NonTerminal.kRule, DomainTag.AXIOM): self.states[3],
      (NonTerminal.kRuleLHS, DomainTag.NTERM): self.states[5],
      (NonTerminal.kRuleLHS, DomainTag.AXIOM): self.states[4],
      (NonTerminal.kRuleR, DomainTag.NTERM): self.states[6],
      (NonTerminal.kRuleR, DomainTag.TERM): self.states[6],
      (NonTerminal.kRuleR, DomainTag.EPS): self.states[6],
      (NonTerminal.kExpr, DomainTag.NTERM): self.states[7],
      (NonTerminal.kExpr, DomainTag.TERM): self.states[7],
      (NonTerminal.kExpr, DomainTag.EPS): self.states[7],
      (NonTerminal.kExpr1, DomainTag.KEY_OR): self.states[8],
      (NonTerminal.kExpr1, DomainTag.KEY_END): self.states[2],
      (NonTerminal.kTerm, DomainTag.NTERM): self.states[9],
      (NonTerminal.kTerm, DomainTag.TERM): self.states[9],
      (NonTerminal.kTerm, DomainTag.EPS): self.states[11],
      (NonTerminal.kTerm1, DomainTag.NTERM): self.states[9],
      (NonTerminal.kTerm1, DomainTag.TERM): self.states[9],
      (NonTerminal.kTerm1, DomainTag.KEY_OR): self.states[2],
      (NonTerminal.kTerm1, DomainTag.KEY_END): self.states[2],
      (NonTerminal.Var, DomainTag.NTERM): self.states[5],
      (NonTerminal.Var, DomainTag.TERM): self.states[10],
    }

  def find(self, non_terminal, tag):
    return self.tableSt.get((non_terminal, tag))

  def err(self, err_str, tok):
    print("(" + str(tok.row) + "," + str(tok.column) + ") " + err_str)


class Parser:
  def __init__(self):
    self.table = AnalyzerTable()

  def TopDownParse(self, scanner: Scanner) -> Node:
    dummy = InnerNode(NonTerminal.kDummy)
    stack = [
      (DomainTag.END_OF_PROGRAM, dummy),
      (NonTerminal.kProgram, dummy),
    ]
    token = scanner.NextToken()
    while stack:
      symbol, parent = stack[-1]

      parent.Output("")
      if isinstance(symbol, DomainTag):
        if token.tag != symbol:
          self.ThrowParseError(token, symbol)
        stack.pop()
        parent.AddChild(LeafNode(token))
        token = scanner.NextToken()
      else:  # symbol is NonTerminal
        if (it := self.table.find(symbol, token.tag)) is not None:
          stack.pop()
          child = InnerNode(symbol)
          parent.AddChild(child)

          sf = it
          for production_symbol in reversed(sf):
            stack.append((production_symbol, child))
        else:
          self.ThrowParseError(token, symbol)

    return dummy.children[0]

  def ThrowParseError(self, token: Token, symbol):
    raise Exception(f"Parse error at token '{token}' expecting {symbol}")


def throw_parse_error(token, expected):
  err = f"{token.coords}: expected {expected}, got {token.tag}"
  raise RuntimeError(err)



```

# Тестирование

Входные данные

```
F  -> "n" 'or "(" E ")" 'end
T  -> F T1 'end
T1 -> "*" F T1 'or 'epsilon 'end
'axiom E  -> T E1 'end
E1 -> "+" T E1 'or 'epsilon 'end

```

Вывод на `stdout`

```
		Program {
		.  Rules {
		.  .  Rule {
		.  .  .  RuleL {
		.  .  .  .  NTERM: F
		.  .  .  }
		.  .  .  OP_ARROW: ->
		.  .  .  RuleR {
		.  .  .  .  Expr {
		.  .  .  .  .  Term {
		.  .  .  .  .  .  Var {
		.  .  .  .  .  .  .  TERM: "n
		.  .  .  .  .  .  }
		.  .  .  .  .  .  Term1 {
		.  .  .  .  .  .  .  Var {
		.  .  .  .  .  .  .  .  TERM: " 
		.  .  .  .  .  .  .  }
		.  .  .  .  .  .  .  Term1 {
		.  .  .  .  .  .  .  }
		.  .  .  .  .  .  }
		.  .  .  .  .  }
		.  .  .  .  .  Expr1 {
		.  .  .  .  .  .  KEY_OR: 'or
		.  .  .  .  .  .  Term {
		.  .  .  .  .  .  .  Var {
		.  .  .  .  .  .  .  .  TERM: "(
		.  .  .  .  .  .  .  }
		.  .  .  .  .  .  .  Term1 {
		.  .  .  .  .  .  .  .  Var {
		.  .  .  .  .  .  .  .  .  TERM: " 
		.  .  .  .  .  .  .  .  }
		.  .  .  .  .  .  .  .  Term1 {
		.  .  .  .  .  .  .  .  .  Var {
		.  .  .  .  .  .  .  .  .  .  NTERM: E
		.  .  .  .  .  .  .  .  .  }
		.  .  .  .  .  .  .  .  .  Term1 {
		.  .  .  .  .  .  .  .  .  .  Var {
		.  .  .  .  .  .  .  .  .  .  .  TERM: ")
		.  .  .  .  .  .  .  .  .  .  }
		.  .  .  .  .  .  .  .  .  .  Term1 {
		.  .  .  .  .  .  .  .  .  .  .  Var {
		.  .  .  .  .  .  .  .  .  .  .  .  TERM: " 
		.  .  .  .  .  .  .  .  .  .  .  }
		.  .  .  .  .  .  .  .  .  .  .  Term1 {
		.  .  .  .  .  .  .  .  .  .  .  }
		.  .  .  .  .  .  .  .  .  .  }
		.  .  .  .  .  .  .  .  .  }
		.  .  .  .  .  .  .  .  }
		.  .  .  .  .  .  .  }
		.  .  .  .  .  .  }
		.  .  .  .  .  .  Expr1 {
		.  .  .  .  .  .  }
		.  .  .  .  .  }
		.  .  .  .  }
		.  .  .  .  KEY_END: 'end
		.  .  .  }
		.  .  }
		.  .  Rules {
		.  .  .  Rule {
		.  .  .  .  RuleL {
		.  .  .  .  .  NTERM: T
		.  .  .  .  }
		.  .  .  .  OP_ARROW: ->
		.  .  .  .  RuleR {
		.  .  .  .  .  Expr {
		.  .  .  .  .  .  Term {
		.  .  .  .  .  .  .  Var {
		.  .  .  .  .  .  .  .  NTERM: F
		.  .  .  .  .  .  .  }
		.  .  .  .  .  .  .  Term1 {
		.  .  .  .  .  .  .  .  Var {
		.  .  .  .  .  .  .  .  .  NTERM: T1
		.  .  .  .  .  .  .  .  }
		.  .  .  .  .  .  .  .  Term1 {
		.  .  .  .  .  .  .  .  }
		.  .  .  .  .  .  .  }
		.  .  .  .  .  .  }
		.  .  .  .  .  .  Expr1 {
		.  .  .  .  .  .  }
		.  .  .  .  .  }
		.  .  .  .  .  KEY_END: 'end
		.  .  .  .  }
		.  .  .  }
		.  .  .  Rules {
		.  .  .  .  Rule {
		.  .  .  .  .  RuleL {
		.  .  .  .  .  .  NTERM: T1
		.  .  .  .  .  }
		.  .  .  .  .  OP_ARROW: ->
		.  .  .  .  .  RuleR {
		.  .  .  .  .  .  Expr {
		.  .  .  .  .  .  .  Term {
		.  .  .  .  .  .  .  .  Var {
		.  .  .  .  .  .  .  .  .  TERM: "*
		.  .  .  .  .  .  .  .  }
		.  .  .  .  .  .  .  .  Term1 {
		.  .  .  .  .  .  .  .  .  Var {
		.  .  .  .  .  .  .  .  .  .  TERM: " 
		.  .  .  .  .  .  .  .  .  }
		.  .  .  .  .  .  .  .  .  Term1 {
		.  .  .  .  .  .  .  .  .  .  Var {
		.  .  .  .  .  .  .  .  .  .  .  NTERM: F
		.  .  .  .  .  .  .  .  .  .  }
		.  .  .  .  .  .  .  .  .  .  Term1 {
		.  .  .  .  .  .  .  .  .  .  .  Var {
		.  .  .  .  .  .  .  .  .  .  .  .  NTERM: T1
		.  .  .  .  .  .  .  .  .  .  .  }
		.  .  .  .  .  .  .  .  .  .  .  Term1 {
		.  .  .  .  .  .  .  .  .  .  .  }
		.  .  .  .  .  .  .  .  .  .  }
		.  .  .  .  .  .  .  .  .  }
		.  .  .  .  .  .  .  .  }
		.  .  .  .  .  .  .  }
		.  .  .  .  .  .  .  Expr1 {
		.  .  .  .  .  .  .  .  KEY_OR: 'or
		.  .  .  .  .  .  .  .  Term {
		.  .  .  .  .  .  .  .  .  EPS: 'epsilon
		.  .  .  .  .  .  .  .  }
		.  .  .  .  .  .  .  .  Expr1 {
		.  .  .  .  .  .  .  .  }
		.  .  .  .  .  .  .  }
		.  .  .  .  .  .  }
		.  .  .  .  .  .  KEY_END: 'end
		.  .  .  .  .  }
		.  .  .  .  }
		.  .  .  .  Rules {
		.  .  .  .  .  Rule {
		.  .  .  .  .  .  RuleL {
		.  .  .  .  .  .  .  AXIOM: 'axiom
		.  .  .  .  .  .  .  NTERM: E
		.  .  .  .  .  .  }
		.  .  .  .  .  .  OP_ARROW: ->
		.  .  .  .  .  .  RuleR {
		.  .  .  .  .  .  .  Expr {
		.  .  .  .  .  .  .  .  Term {
		.  .  .  .  .  .  .  .  .  Var {
		.  .  .  .  .  .  .  .  .  .  NTERM: T
		.  .  .  .  .  .  .  .  .  }
		.  .  .  .  .  .  .  .  .  Term1 {
		.  .  .  .  .  .  .  .  .  .  Var {
		.  .  .  .  .  .  .  .  .  .  .  NTERM: E1
		.  .  .  .  .  .  .  .  .  .  }
		.  .  .  .  .  .  .  .  .  .  Term1 {
		.  .  .  .  .  .  .  .  .  .  }
		.  .  .  .  .  .  .  .  .  }
		.  .  .  .  .  .  .  .  }
		.  .  .  .  .  .  .  .  Expr1 {
		.  .  .  .  .  .  .  .  }
		.  .  .  .  .  .  .  }
		.  .  .  .  .  .  .  KEY_END: 'end
		.  .  .  .  .  .  }
		.  .  .  .  .  }
		.  .  .  .  .  Rules {
		.  .  .  .  .  .  Rule {
		.  .  .  .  .  .  .  RuleL {
		.  .  .  .  .  .  .  .  NTERM: E1
		.  .  .  .  .  .  .  }
		.  .  .  .  .  .  .  OP_ARROW: ->
		.  .  .  .  .  .  .  RuleR {
		.  .  .  .  .  .  .  .  Expr {
		.  .  .  .  .  .  .  .  .  Term {
		.  .  .  .  .  .  .  .  .  .  Var {
		.  .  .  .  .  .  .  .  .  .  .  TERM: "+
		.  .  .  .  .  .  .  .  .  .  }
		.  .  .  .  .  .  .  .  .  .  Term1 {
		.  .  .  .  .  .  .  .  .  .  .  Var {
		.  .  .  .  .  .  .  .  .  .  .  .  TERM: " 
		.  .  .  .  .  .  .  .  .  .  .  }
		.  .  .  .  .  .  .  .  .  .  .  Term1 {
		.  .  .  .  .  .  .  .  .  .  .  .  Var {
		.  .  .  .  .  .  .  .  .  .  .  .  .  NTERM: T
		.  .  .  .  .  .  .  .  .  .  .  .  }
		.  .  .  .  .  .  .  .  .  .  .  .  Term1 {
		.  .  .  .  .  .  .  .  .  .  .  .  .  Var {
		.  .  .  .  .  .  .  .  .  .  .  .  .  .  NTERM: E1
		.  .  .  .  .  .  .  .  .  .  .  .  .  }
		.  .  .  .  .  .  .  .  .  .  .  .  .  Term1 {
		.  .  .  .  .  .  .  .  .  .  .  .  .  }
		.  .  .  .  .  .  .  .  .  .  .  .  }
		.  .  .  .  .  .  .  .  .  .  .  }
		.  .  .  .  .  .  .  .  .  .  }
		.  .  .  .  .  .  .  .  .  }
		.  .  .  .  .  .  .  .  .  Expr1 {
		.  .  .  .  .  .  .  .  .  .  KEY_OR: 'or
		.  .  .  .  .  .  .  .  .  .  Term {
		.  .  .  .  .  .  .  .  .  .  .  EPS: 'epsilon
		.  .  .  .  .  .  .  .  .  .  }
		.  .  .  .  .  .  .  .  .  .  Expr1 {
		.  .  .  .  .  .  .  .  .  .  }
		.  .  .  .  .  .  .  .  .  }
		.  .  .  .  .  .  .  .  }
		.  .  .  .  .  .  .  .  KEY_END: 'end
		.  .  .  .  .  .  .  }
		.  .  .  .  .  .  }
		.  .  .  .  .  .  Rules {
		.  .  .  .  .  .  }
		.  .  .  .  .  }
		.  .  .  .  }
		.  .  .  }
		.  .  }
		.  }
		}
```

# Вывод

В данной работе был изучен алгоритм построения таблиц предсказывающего анализатора
и разработан синтаксический анализатор на основе предсказывающего анализа для входного языка.

Для построения таблицы предсказывающего анализа был составлен набор правил грамматики входного языка. 
Для каждого правила было определено множество first, которое представляет собой множество 
терминальных символов, которые могут появляться в начале вывода этого правила.

Затем была построена таблица предсказывающего анализа. Для каждой пары состояние автомата - символ входного 
алфавита в таблице указывалось действие, которое должно быть выполнено. Действие определялось на основе 
first множества правила, соответствующего состоянию автомата.

Данная работа позволила вспомнить лабораторную работу по курсу теория формальных языков,
но с отличием того, что в прошлом курсе приходилось программно реализовывать алгоритм
построения first множества и строить таблицы, осознание и реализация которых требовало внушительного 
количества времени раньше.