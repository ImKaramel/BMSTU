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
