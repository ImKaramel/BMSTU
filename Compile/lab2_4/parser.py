import tag
from node import Program, FuncHeader, Func, FuncParams, BasicVar, Statements, ReturnStatement, WarningStatement, \
    FuncCall, AssignmentStatement, VarDeclarationStatement, ForStatement, IfStatement, WhileStatement, Cycle, BinOpExpr, \
    AllocExpr, ConstExpr, FuncBody, ArrType, VarType, VarExpr
from scanner import Scanner



class Parser:
    def __init__(self, scanner: Scanner):
        self.sym = scanner.NextToken()
        self.scanner = scanner


    def ExpectTags(self, *tags):
        for tag in tags:
            if self.sym.tag == tag:
                sym = self.sym
                self.sym = self.scanner.NextToken()
                if self.sym.tag == "ERR":
                    raise Exception("parse error: unexpected token")
                return sym

        raise Exception("parse error: expected {}, but got {}".format(tags, self.sym))

    # Program -> (Func) +
    def program(self):
        funcs = []
        funcs.append(self.Func())
        while self.sym.val == "[" or self.sym.val == "(":
            funcs.append(self.Func())

        return Program(funcs)


    def ExpectStr(self, *vals):
        for val in vals:

            if self.sym.val == val:
                sym = self.sym

                self.sym = self.scanner.NextToken()

                if self.sym.tag == tag.DomainTag.ERR:
                    raise Exception("parse error: unexpected token")
                return sym

        raise Exception(f"parse error: expected {vals}, but got {self.sym.val}, {str(self.sym.coord)}")

#  Func ->  FuncHeader FuncBody
    def Func(self):
        header = self.FuncHeader()
        body = self.FuncBody()

        return Func(header, body)

    # Type -> '<' Type '>' | 'int' | 'bool' | 'char'
    def Type(self):
        if self.sym.val == "<":
            self.ExpectStr("<")
            t = self.Type()
            self.ExpectStr(">")
            return ArrType(t)
        varT = self.ExpectStr("int", "bool", "char")
        return VarType(varT)


    #FuncHeader -> "(" Type "[" FUNCNAME FuncParams "]" ")"
    #FuncHeader -> "[" FUNCNAME FuncParams "]"
    def FuncHeader(self):
        if self.sym.val == "(":
            self.ExpectStr("(")
            t = self.Type()

            self.ExpectStr("[")
            funcName = self.ExpectTags(tag.DomainTag.FUNCNAME)
            params = self.FuncParams()
            self.ExpectStr("]")
            self.ExpectStr(")")
            return FuncHeader(t, funcName, params)

        self.ExpectStr("[")
        funcName = self.ExpectTags(tag.DomainTag.FUNCNAME)
        params = self.FuncParams()
        self.ExpectStr("]")
        return FuncHeader(None, funcName, params)

# FuncBody -> Statements "%%"
    def FuncBody(self):
        statements = self.Statements()
        self.ExpectStr("%%")
        return FuncBody(statements)


#FuncParams -> (BasicVar)*
    def FuncParams(self):
        basicVars = []
        while self.sym.val == "(":
            basicVars.append(self.BasicVar())

        return FuncParams(basicVars)


#BasicVar -> "(" Type VARNAME ")"
    def BasicVar(self):
        self.ExpectStr("(")
        t = self.Type()
        varname = self.ExpectTags(tag.DomainTag.VARNAME)
        self.ExpectStr(")")

        return BasicVar(t, varname)


#Statements -> Statement ("," Statement)*
    def Statements(self):
        statement = []
        statement.append(self.Statement())
        while self.sym.val == ",":
            self.ExpectStr(",")
            statement.append(self.Statement())

        return Statements(statement)


    #   Statement -> "^" Expr
    #   Statement -> "\\" Expr
    #   Statement -> Var ":=" Expr
    #   Statement -> "[" FUNCNAME Args "]"
    #   Statement -> "(" StatementTail
    def Statement(self):
        if self.sym.val == "^":
            self.ExpectStr("^")
            expr = self.Expr()
            return ReturnStatement(expr)
        elif self.sym.val == "\\":
            self.ExpectStr("\\")
            expr = self.Expr()
            return WarningStatement(expr)
        elif self.sym.val == "[":
            self.ExpectStr("[")
            funcName = self.ExpectTags(tag.DomainTag.FUNCNAME)
            args = self.Args()
            self.ExpectStr("]")
            return FuncCall(funcName, args)
        elif self.sym.tag == tag.DomainTag.VARNAME or self.sym.val == "<":
            v = self.Var()
            self.ExpectStr(":=")
            expr = self.Expr()
            return AssignmentStatement(v, expr)
        else:
            self.ExpectStr("(")
            return self.StatementTail()


    #  StatementTail -> Type VARNAME ((")" (":=" Expr)?) | (Cycle Statements "%"))
    #  StatementTail -> "&" Expr ")" Statements "%"
    #  StatementTail -> "?" Expr ")" Statements ("+++" Statements)? "%"
    def StatementTail(self):
        if self.sym.val == "<" or self.sym.val == "int" or self.sym.val == "bool" or self.sym.val == "char":
            t = self.Type()
            varname = self.ExpectTags(tag.DomainTag.VARNAME)
            if self.sym.val == ")":
                self.ExpectStr(")")
                if self.sym.val == ":=":
                    self.ExpectStr(":=")
                    expr = self.Expr()
                    return AssignmentStatement(ConstExpr(t, varname), expr)
                return VarDeclarationStatement(t, varname)
            elif self.sym.val == ":":
                cycle = self.Cycle()
                statements = self.Statements()
                self.ExpectStr("%")
                return ForStatement(t, varname, cycle.start, cycle.end, cycle.step, statements)
            else:
                raise Exception("parse error")
        elif self.sym.val == "?":
            self.ExpectStr("?")
            expr = self.Expr()
            self.ExpectStr(")")
            thenBranch = self.Statements()
            elseBranch = None
            if self.sym.val == "+++":
                self.ExpectStr("+++")
                elseBranch_ = self.Statements()
                elseBranch = elseBranch_
            self.ExpectStr("%")
            return IfStatement(expr, thenBranch, elseBranch)
        else:
            self.ExpectStr("&")
            expr = self.Expr()
            self.ExpectStr(")")
            statements = self.Statements()
            self.ExpectStr("%")
            return WhileStatement(expr, statements)

    # Cycle -> VARNAME ":" Expr "," Expr ("," INT_CONST)? ")"

    def Cycle(self):
        self.ExpectStr(":")
        startExpr = self.Expr()
        self.ExpectStr(",")
        endExpr = self.Expr()
        step = None
        if self.sym.val == ",":
            self.ExpectStr(",")
            token_ = self.ExpectTags(tag.DomainTag.INT_CONST)
            step = token_
        self.ExpectStr(")")

        return Cycle(startExpr, endExpr, step)

    #Args -> (Spec)+

    def Args(self):
        specs = []
        specs.append(self.Spec())
        while self.sym.val == "(" or self.sym.val == "[" or self.sym.val == "<" or self.sym.val == "new_" \
                or self.sym.val == "true" or self.sym.val == "false" or self.sym.tag == tag.DomainTag.INT_CONST\
                or self.sym.tag == tag.DomainTag.CHAR_CONST or self.sym.tag == tag.DomainTag.STRING_CONST\
                or self.sym.tag == tag.DomainTag.VARNAME:
            specs.append(self.Spec())

        return specs

    # Expr -> LogicalExpr ((_or_ | _xor_) LogicalExpr)*

    def Expr(self):
        expr = self.LogicalExpr()
        while self.sym.val == "_or_" or self.sym.val == "_xor_":
            op = self.ExpectStr("_or_", "_xor_")
            rightExpr = self.LogicalExpr()
            expr = BinOpExpr(expr, op, rightExpr)

        return expr

    # LogicalExpr -> CompareExpr (_and_ CompareExpr)*
    def LogicalExpr(self):
        expr = self.CompareExpr()
        while self.sym.val == "_and_":
            op = self.ExpectStr("_and_")
            rightExpr = self.CompareExpr()
            expr = BinOpExpr(expr, op, rightExpr)

        return expr


    #CompareExpr -> ArithmExpr (CmpOp ArithmExpr)*
    def CompareExpr(self):
        expr = self.ArithmExpr()
        if self.sym.val == "_eq_" or self.sym.val == "_ne_" or self.sym.val == "_lt_"\
                or self.sym.val == "_gt_" or self.sym.val == "_le_" or self.sym.val == "_ge_":
            op = self.CmpOp()
            rightExpr = self.ArithmExpr()

            expr = BinOpExpr(expr, op, rightExpr)

        return expr

    def CmpOp(self):
        return self.ExpectStr("_eq_", "_ne_", "_lt_", "_gt_", "_le_", "_ge_")


    # ArithmExpr -> PowExpr (("+" | "-")  PowExpr)*
    def ArithmExpr(self):
        expr = self.PowExpr()
        while self.sym.val == "+" or self.sym.val == "-":
            op = self.ExpectStr("+", "-")
            rightExpr = self.PowExpr()

            expr = BinOpExpr(expr, op, rightExpr)

        return expr


    #PowExpr -> Term (_pow_ PowExpr)?
    def PowExpr(self):
        expr = self.Term()
        if self.sym.val == "_pow_":
            op = self.ExpectStr("_pow_")
            rightExpr = self.PowExpr()
            expr = BinOpExpr(expr, op, rightExpr)

        return expr


    # Term -> Factor (("*" | "/" | _mod_) Factor)*
    def Term(self):
        expr = self.Factor()
        while self.sym.val == "*" or self.sym.val == "/" or self.sym.val == "_mod_":
            op = self.ExpectStr("*", "/", "_mod_")
            rightExpr = self.Factor()
            return BinOpExpr(expr, op, rightExpr)

        return expr


    #  Factor -> (not_ | "-")? Spec

    def Factor(self):
        if self.sym.val == "not_":
            self.ExpectStr("not_")
        elif self.sym.val == "-":
            self.ExpectStr("-")

        return self.Spec()


    #FuncCall -> "[" FUNCNAME Args "]"

    def FuncCall(self):
        self.ExpectStr("[")
        funcname = self.ExpectTags(tag.DomainTag.FUNCNAME)
        args = self.Args()
        self.ExpectStr("]")

        return FuncCall(funcname, args)

    # Spec -> FuncCall
    # Spec -> new_ Type(VARNAME | INT_CONST)
    # Spec -> Const
    # Spec -> Var
    # Spec -> "("Expr")"
    def Spec(self):
        if self.sym.val == "(":
            self.ExpectStr("(")
            expr = self.Expr()
            self.ExpectStr(")")
            return expr
        elif self.sym.val == "<" or self.sym.tag == tag.DomainTag.VARNAME:
            varExpr = self.Var()
            return varExpr
        elif self.sym.val == "true" or self.sym.val == "false" or self.sym.val == "nothing"\
                or self.sym.tag == tag.DomainTag.INT_CONST or self.sym.tag == tag.DomainTag.CHAR_CONST\
                or self.sym.tag == tag.DomainTag.STRING_CONST:
            return self.Const()
        elif self.sym.val == "[":
            return self.FuncCall()
        else:
            self.ExpectStr("new_")
            t = self.Type()
            size = self.ExpectTags(tag.DomainTag.VARNAME, tag.DomainTag.INT_CONST)
            return AllocExpr(t, size)


    #Var -> VARNAME | "<" Spec Expr ">"
    def Var(self):
        if self.sym.val == "<":
            self.ExpectStr("<")
            arrayName = self.Spec()
            expr = self.Expr()
            self.ExpectStr(">")
            return VarExpr(None, arrayName, expr)

        varname = self.ExpectTags(tag.DomainTag.VARNAME)
        # return VarExpr()
        return VarExpr(varname, None, None)

    #Const → INT_CONST | CHAR_CONST | STRING_CONST | REF_CONST | BOOL_CONST

    def Const(self):
        if self.sym.tag == tag.DomainTag.INT_CONST or self.sym.tag == tag.DomainTag.CHAR_CONST\
                or self.sym.tag == tag.DomainTag.STRING_CONST:
            val = self.ExpectTags(tag.DomainTag.INT_CONST, tag.DomainTag.CHAR_CONST, tag.DomainTag.STRING_CONST)
            return ConstExpr(None, val)
        str = self.ExpectStr("true", "false", "nothing")
        return ConstExpr(None, str)
