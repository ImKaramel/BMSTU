sealed trait Expr

case class Variable(name: String) extends Expr

case class NUMBER(value: Int) extends Expr

case class C(attr: String, arguments: List[Expr] = List.empty[Expr]) extends Expr {
  def apply(exprs: Expr*): C = {
    copy(arguments = arguments ++ exprs.toList)
  }
}

object Main {
  implicit def intToNumber(value: Int): NUMBER = NUMBER(value)
  def main(args: Array[String]): Unit = {
    val X: Variable = Variable("X")
    val Y: Variable = Variable("Y")
    val Z: Variable = Variable("Z")
    val S: Variable = Variable("S")

    val Cons: C = C("Cons")
    val Nil: C = C("Nil")

    val expr1 = Cons(Y, S, Cons(5, Cons(3, Nil())))
    val expr2 = Cons(X, Z, Cons(5, Cons(3, Nil())))
    val result = unify(expr1, expr2)
    println(result)
    val expr3 = X
    val expr4 = 1
    val result3 = unify(expr3, expr4)
     println(result3)
    
    val Tree: C = C("Tree")
    val Leaf: C = C("Leaf")
    val expr5 = Tree(Leaf(), 1, Tree(Leaf(), 2, Leaf()))
  }

  def unify(expr1: Expr, expr2: Expr): Option[Map[String, Expr]] = {
    (expr1, expr2) match {
      case (C(attr1, args1), C(attr2, args2)) if attr1 == attr2 =>
        unifyList(args1, args2)
      case (NUMBER(n1), NUMBER(n2)) if n1 == n2 => Some(Map.empty)
      case (Variable(name1), Variable(name2)) if name1 == name2 =>
        Some(Map.empty)
      case (Variable(name), expr) =>
        unifyVariable(name, expr)
      case (expr, Variable(name)) =>
        unifyVariable(name, expr)
      case _ =>
        None
    }
  }

  def unifyList(list1: List[Expr], list2: List[Expr]): Option[Map[String, Expr]] = {
    (list1, list2) match {
      case (Nil, Nil) =>
        Some(Map.empty)
      case (head1 :: tail1, head2 :: tail2) =>
        unify(head1, head2) match {
          case Some(subst1) =>
            unifyList(applySubstitution(tail1, subst1), applySubstitution(tail2, subst1)) match {
              case Some(subst2) =>
                combineSubstitutions(subst1, subst2)
              case None =>
                None
            }
          case None =>
            None
        }
      case _ =>
        None
    }
  }

  def unifyVariable(name: String, expr: Expr): Option[Map[String, Expr]] = {
    if (isVar(expr, name)) {
      None
    } else {
      Some(Map(name -> expr))
    }
  }

  def applySubstitution(exprs: List[Expr], substitution: Map[String, Expr]): List[Expr] = {
    exprs.map(applySubstitution(_, substitution))
  }

  def applySubstitution(expr: Expr, substitution: Map[String, Expr]): Expr = {
    expr match {
      case Variable(name) =>
        substitution.getOrElse(name, expr)
      case C(attr, args) =>
        C(attr, applySubstitution(args, substitution))
      case _ =>
        expr
    }
  }

  def combineSubstitutions(subst1: Map[String, Expr], subst2: Map[String, Expr]): Option[Map[String, Expr]] = {
    val combined = subst1 ++ subst2
    if (combined.size == subst1.size + subst2.size) {
      Some(combined)
    } else {
      None
    }
  }

  def isVar(expr: Expr, name: String): Boolean = {
    expr match {
      case Variable(n) if n == name =>
        true
      case C(_, args) =>
        args.exists(isVar(_, name))
      case _ =>
        false
    }
  }
}
