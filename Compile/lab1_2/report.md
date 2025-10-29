% Лабораторная работа № 1.2. «Лексический анализатор
  на основе регулярных выражений»
% 12 марта 2024 г.
% Ольга Александрова, ИУ9-61Б

# Цель работы
Целью данной работы является приобретение навыка разработки простейших лексических анализаторов,
работающих на основе поиска в тексте по образцу, заданному регулярным выражением.

# Индивидуальный вариант
Комментарии: целиком строка текста, начинающаяся с `*`.
Идентификаторы: либо последовательности латинских букв нечётной длины, либо последовательности символов `*`.
Ключевые слова: `with`, `end`, `**`.

# Реализация

```python
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
```
# Тестирование
Входные данные

*123 'test' 45

** tyu "fggv" * ttt3t with end t

*** hhhhh

Вывод на `stdout`

``` 
('COMMENT', (1, 0), "*123 'test' 45")
('KEYWORD', (2, 0), '**')
('IDENT', (2, 3), 'tyu')
('ERROR', (2, 7), '"fggv"')
('ERROR', (2, 14), '*')
('ERROR', (2, 16), 'ttt3t')
('KEYWORD', (2, 22), 'with')
('KEYWORD', (2, 27), 'end')
('IDENT', (2, 31), 't')
('IDENT', (3, 0), '***')
('IDENT', (3, 4), 'hhhhh')
```

# Вывод

В данной лабораторной работе были приобретены навыки работы с 
регулярными выражениями, с помощью которых был написан лексический анализатор.
Для реализации была изучена и успешно применена библиотека ```re``` в ```python```.