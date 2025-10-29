import re

class Tokenizer:
    def __init__(self, text):
        self.text = text
        self.keywords = ['with', 'end', '**']
        self.patterns = {
            'KEYWORD': r'(with|end|\*\*)',
            'COMMENT': r'\*[^*]?',
            'IDENT': r'(?:[a-zA-Z]{2})*[a-zA-Z]|[\*][\*]+'
        }
        self.tokens = self.tokenize()

    def tokenize(self):
        tokens = []
        lines = self.text.split("\n")
        num = 0

        for line in lines:
            num += 1
            pos = 0
            if line.count('*') == 1 and line[0] == '*':
                match_comment = re.match(self.patterns['COMMENT'], line)
                if match_comment:
                    tokens.append(('COMMENT', (num, pos), line))
                    pos += len(line)
            else:
                words = line.split()
                for word in words:
                    for name, pattern in self.patterns.items():
                        if re.fullmatch(pattern, word):
                            if name != 'COMMENT':
                                tokens.append((name, (num, pos), word))
                                break
                    else:
                        tokens.append(('ERROR', (num, pos), word))
                    pos += len(word) + 1

        return tokens

    def nextToken(self):
        if self.tokens:
            return self.tokens.pop(0)
        else:
            return None


if __name__ == '__main__':
    with open('input.txt', 'r') as file:
        text = file.read()
    tokenizer = Tokenizer(text)
    for _ in range(len(tokenizer.tokens)):
        token = tokenizer.nextToken()
        print(token)


# pandoc \
#   --pdf-engine=xelatex \
#   -V 'mainfont:Liberation Serif' \
#   -V 'monofont:Liberation Mono' \
#   report.md -o out.pdf


