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
            # print(indent + "\tArrayElemByIndex: " + str(self.varName.val))
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
