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
        print(self.text[self.index])
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



