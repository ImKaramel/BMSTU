from typing import List

class Node:
    def Output(self, kIndent):
        raise NotImplementedError()

class InnerNode(Node):
    def __init__(self, non_terminal: str):
        self.non_terminal = non_terminal
        self.children: List[Node] = []

    def Output(self, indent: str):
        output = f"{indent}{self.non_terminal} {{\n"
        for child in self.children:
            output += child.Output(indent + ".  ")
        output += f"{indent}}}\n"
        return output

    def AddChild(self, node: Node):
        self.children.append(node)
        return self.children[-1]


class LeafNode(Node):
    def __init__(self, token):
        self.token = token

    def Output(self, indent: str):
        return f"{indent}{self.token.tag}: {self.token.val}\n"


class NonTerminal:
    kProgram = "Program"
    kRules = "Rules"
    kRule = "Rule"
    kRuleL = "RuleL"
    kRuleR = "RuleR"
    kExpr = "Expr"
    kExpr1 = "Expr1"
    kTerm = "Term"
    kTerm1 = "Term1"
    Var = "Var"
    kDummy = "Dummy"
