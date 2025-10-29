% Лабораторная работа № 1.3 «Объектно-ориентированный
  лексический анализатор»
% 20 марта 2024 г.
% Ольга Александрова, ИУ9-61Б

# Цель работы
Целью данной работы является приобретение навыка реализации лексического анализатора
на объектно-ориентированном языке без применения каких-либо средств автоматизации 
решения задачи лексического анализа.

# Индивидуальный вариант
Географические координаты: начинаются с одного из знаков «S», «E», «N», «W», после которых 
располагается целое десятичное число, за которым может следовать либо точка и 
последовательность десятичных цифр, либо знак «D», за которым следует 
необязательная запись угловых минут (число от 0 до 59, за которым пишется апостроф)
и угловых секунд (число от 0 до 59, за которым следует двойная кавычка). Атрибут лексемы
(для лабораторных работ 1.3 и 1.5): вещественное число, соответствующее широте или долготе. Широта («S», «N»)
не может превышать 90, долгота («E», «W») — 180.

# Реализация

Файл `Position.py`
```python
class Position:
    def __init__(self, text, i=0, l=1, c=1):
        self.text = text
        self.line = l
        self.pos = c
        self.index = i

    def Line(self):
        return self.line

    def Pos(self):
        return self.pos

    def Index(self):
        return self.index

    def CompareTo(self, other):
        return self.index - other.index

    def __str__(self):
        return f"({self.line},{self.pos})"

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
        valid_letters = {'S', 'N', 'W', 'E'}
        return self.index != len(self.text) and self.text[self.index] in valid_letters

    def isSpecialSymbol(self):
        valid_symbols = {'D', '.'}
        return self.index != len(self.text) and self.text[self.index] in valid_symbols

    def isDot(self):
        return self.index != len(self.text) and self.text[self.index] == '.'

    def isD(self):
        return self.index != len(self.text) and self.text[self.index] == 'D'

    def IsDecimalDigit(self):
        return self.index != len(self.text) and self.text[self.index].isdigit()

    def isNewLine(self):
        if self.index == len(self.text):
            return True
        if (self.text[self.index] == '\r') and (self.index + 1 < len(self.text)):
            return self.text[self.index + 1] == '\n'
    
        return self.text[self.index] == '\n'

    def skip(self):
        if self.index < len(self.text):
            if self.isNewLine():
                i = self.index
                l = self.line + 1
                return Position(self.text, i + 1, l, 1)
            else:
                i = self.index
                if self.text[i] == '\ud800':
                    i = i + 1

                c = self.pos + 1
                return Position(self.text, i + 1, self.line, c)
        return self
```

Файл `Token.py`
```python
class Token:
    def __init__(self, tag, starting, following):
        self.Tag = tag
        self.Coords = Fragment(starting, following)


class LongToken(Token):
    def __init__(self, code, starting, following):
        super().__init__(DomainTag.LONG, starting, following)
        self.Code = code

    def print(self):
        print(str(self.Tag) + str(self.Coords) + ": " + str(self.Code))


class LatitudeToken(Token):
    def __init__(self, val, starting, following):
        super().__init__(DomainTag.LATITUDE, starting, following)
        self.Code = val

    def print(self):
        print(str(self.Tag) + str(self.Coords) + ": " + str(self.Code))


class ErrToken(Token):
    def __init__(self, s):
        super().__init__(DomainTag.ERR, s, s)

    def print(self):
        pass


class EndToken(Token):
    def __init__(self, s, f):
        super().__init__(DomainTag.END, s, f)

    def print(self):
        pass
```

Файл `Fragment.py`
```python
class Fragment:
    def __init__(self, starting, following):
        self.Starting = starting
        self.Following = following

    def __str__(self):
        return str(self.Starting) + "-" + str(self.Following)


class Message:
    def __init__(self, isError, text):
        self.IsError = isError
        self.Text = text
```

Файл `Compile.py`
```python
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
```

Файл `Scanner.py`

```python
class Scanner:
    def __init__(self, program: str, compiler: Compiler):
        self.Program = program
        self.compiler = compiler
        self.cur = Position(self.Program)

    def NextToken(self):
        while self.cur.Cp() != -1:
            while self.cur.IsWhiteSpace():
                self.cur = self.cur.skip()

            start = self.cur
            if self.cur.IsLetter():
                self.cur = self.cur.skip()

                name = self.Program[start.Index():self.cur.Index()]

                start = self.cur
                while self.cur.IsDecimalDigit():
                    self.cur = self.cur.skip()
                num_str = self.Program[start.Index():self.cur.Index()]

                if self.cur.isSpecialSymbol():
                    if self.cur.isDot():
                        num_str += '.'
                        self.cur = self.cur.skip()
                        start2 = self.cur
                        while self.cur.IsDecimalDigit():
                            self.cur = self.cur.skip()
                        num_str += self.Program[start2.Index():self.cur.Index()]
                        degrees = float(num_str)
                    else:
                        degrees = float(num_str)
                        self.cur = self.cur.skip()
                        start2 = self.cur
                        while self.cur.IsDecimalDigit():
                            self.cur = self.cur.skip()

                        if self.Program[self.cur.Index()] == '`':
                            minutes = float(self.Program[start2.Index():(self.cur.Index())])
                            if (minutes >= 0) and (minutes <= 59):
                                degrees += minutes / 60
                            else:
                                self.compiler.AddMessage(True, start2, "invalid value for minutes")

                            self.cur = self.cur.skip()
                            start2 = self.cur
                            while self.cur.IsDecimalDigit():
                                self.cur = self.cur.skip()
                            if self.cur.Cp() == '"':

                                sec = float(self.Program[start2.Index():(self.cur.Index())])
                                if (sec >= 0) and (sec <= 59):
                                    degrees += sec / 3600
                                else:
                                    self.compiler.AddMessage(True, start2, "invalid value for seconds")
                                self.cur = self.cur.skip()

                        if self.Program[self.cur.Index()] == '"':
                            degrees += float(self.Program[start2.Index():(self.cur.Index())]) / 3600
                            self.cur = self.cur.skip()

                    if name in {'E', 'W'}:
                        if degrees <= 180:
                            return LongToken(degrees, start, self.cur)
                        else:
                            self.compiler.AddMessage(True, start, "invalid coordinates range for LONG")
                    else:
                        if degrees <= 90:
                            return LatitudeToken(degrees, start, self.cur)
                        else:

                            self.compiler.AddMessage(True, start, "invalid coordinates range for Latitude")
                else:
                    self.compiler.AddMessage(True, start, "invalid coordinates EXPECTED D or .")
            else:
                self.compiler.AddMessage(True, start, "unexpected symbol."
                                                "Coordinate should start with Letter")
                self.cur = self.cur.skip()
        return EndToken(self.cur, self.cur)
```
# Тестирование

Входные данные

```
S11.19 E123D1`
        E123D123" S123.123"
```

Вывод на `stdout`

```
DomainTag.LATITUDE(1,2)-(1,7): 11.19
DomainTag.LONG(1,9)-(1,15): 123.01666666666667
DomainTag.LONG(2,10)-(2,18): 123.03416666666666
Error (2,20): invalid coordinates range for Latitude
Error (2,27): unexpected symbol. Coordinate should start with Letter
```

# Вывод
После реализации лексического анализатора на объектно-ориентированном языке программирования
без использования средств автоматизации были приобретены следующие навыки:
1. Понимание основ работы лексического анализа.
2. Умение разрабатывать структуры данных для хранения токенов, таблиц идентификаторов, комментариев и ошибок.
3. Умение создавать чистые функции и методы, принимающие входные данные и возвращающие
результирующую информацию.

Это задание позволило углубить знания в области разработки компиляторов, повысить уровень
владения объектно-ориентированным (`Python`) языком программирования, а также освоить практические 
навыки реализации лексического анализатора без использования средств автоматизации.
