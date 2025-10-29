from node import Node, NonTerminal, LeafNode, InnerNode
from src.tok import DomainTag, Token
from scanner import Scanner


class AnalyzerTable:
    def __init__(self):
        self.states = [
            [NonTerminal.kRules],  # 0
            [NonTerminal.kRule, NonTerminal.kRules],  # 1
            [],  # 2
            [NonTerminal.kRuleL, DomainTag.OP_ARROW, NonTerminal.kRuleR],  # 3
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
            (NonTerminal.kRuleL, DomainTag.NTERM): self.states[5],
            (NonTerminal.kRuleL, DomainTag.AXIOM): self.states[4],
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


