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
                if not self.curPos.isNewLine() and self.curPos.Cp() != -1 and self.curPos.GetSymbol() != '"':
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
                while self.curPos.Cp() != -1 and self.curPos.GetSymbol() != '\'' and not self.curPos.isNewLine():
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
                if not self.curPos.isNewLine() and not self.curPos.IsWhiteSpace() and self.curPos.Cp() != -1:
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
                while not self.curPos.isNewLine() and self.curPos.Cp() != -1 and self.curPos.GetSymbol() != '}':
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
                if not self.curPos.IsCloseBracket() and not self.curPos.isNewLine() and not self.curPos.IsWhiteSpace()\
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
                                and not self.curPos.isNewLine() and not self.curPos.IsWhiteSpace() and self.curPos.Cp() != -1:
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
