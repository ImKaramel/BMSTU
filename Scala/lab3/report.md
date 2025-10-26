% Лабораторная работа № 3 «Обобщённые классы в Scala»
% 17 апреля 2024 г.
% Ольга Александрова, ИУ9-61Б

# Цель работы
Целью данной работы является приобретение навыков разработки обобщённых классов на языке Scala с 
использованием неявных преобразований типов.

# Индивидуальный вариант
Класс SuperNumber[T], представляющий число произвольной разрядности в системе счисления, цифрами 
которой выступают значения типа T. Если T — целочисленный тип Scala или Bool, то для SuperNumber[T]
должна быть доступна операция сложения. 
Если T — Bool, то дополнительно должны работать операции поразрядного И и ИЛИ.

# Реализация

```scala
trait DigitOps[T] {
  def add(a: T, b: T): (T, T)
}

//   Int
implicit object IntDigitOps extends DigitOps[Int] {
  override def add(a: Int, b: Int): (Int, Int) = {
    val sum = a + b
    val maxInt = Int.MaxValue
    val k1 = maxInt - a
    if (k1 - b >= 0) {
        val sum = a + b
        (sum, 0)
    } else {
        val overflow = b - k1
        (overflow, 1)
    }
  }
}

//  Long
implicit object LongDigitOps extends DigitOps[Long] {
  override def add(a: Long, b: Long): (Long, Long) = {
    val sum = a + b
    val maxLong = Long.MaxValue
    val k1 = maxLong - a
    if (k1 - b >= 0) {
        val sum = a + b
        (sum, 0L)
    } else {
        val overflow = b - k1
        (overflow, 1)
    }
  }
}

//Boolean
implicit object BooleanDigitOps extends DigitOps[Boolean] {
  override def add(a: Boolean, b: Boolean): (Boolean, Boolean) = {
    val sum =   ((a || b) && !(a && b))   
    val overflow = if (a && b) true else false  
    (sum, overflow)
  }
}

class SuperNumber[T](digits: List[T]) {
  def length: Int = digits.length
  def getDigits: List[T] = digits
  override def toString: String = digits.mkString(" ")

  private def normalBool[T](list1: List[T], list2: List[T]):
         (List[Boolean], List[Boolean]) = {
    val maxLength = list1.length max list2.length
    val normdList1 = list1.reverse.padTo(maxLength, false).reverse
    val normdList2 = list2.reverse.padTo(maxLength, false).reverse
    (normdList1.map(_.asInstanceOf[Boolean]), normdList2.map(_.asInstanceOf[Boolean]))
  }

  def &(other: SuperNumber[T]): SuperNumber[Boolean] = {
    val (num1, num2) = normalBool(digits, other.getDigits)
    val result = num1.zip(num2).map {
      case (x, y) => x && y
    }
    new SuperNumber[Boolean](result)
  }

  def |(other: SuperNumber[T]): SuperNumber[Boolean] = {
    val (num1, num2) = normalBool(digits, other.getDigits)
    val result = num1.zip(num2).map {
      case (x, y) => x || y
    }
    new SuperNumber[Boolean](result)
  }

  def + (other: SuperNumber[T])(implicit op: DigitOps[T]): SuperNumber[T] = {
    val thisDigits = this.getDigits.reverse  
    val otherDigits = other.getDigits.reverse
     
    def sumLists(a: List[T], b: List[T], carry: T, acc: List[T]): List[T] = (a, b) match {
        case (Nil, Nil) => if (carry != 0) List(carry) ++ acc else acc
        case (Nil, bh :: bt) => 
            val (result, newCarry) = op.add(carry, bh)
            sumLists(Nil, bt, newCarry,  result :: acc)
        case (ah :: at, Nil) => 
            val (result, newCarry) = op.add(carry, ah)
            sumLists(at, Nil, newCarry, result :: acc)
        case (ah :: at, bh :: bt) =>
            val (result, newCarry) = op.add(ah, bh)
            val (res, _) = op.add(result, carry)
             
            sumLists(at, bt, newCarry,   res :: acc)
    }


    val result = sumLists(thisDigits, otherDigits, null.asInstanceOf[T], Nil)
    new SuperNumber[T](result)  
  }
}
object Main {
 
  def main(args: Array[String]): Unit = {

    val superNum1 = new SuperNumber[Int](List(1870090000, 2, 3))  
    val superNum2 = new SuperNumber[Int](List(4, 588000090, 6, 7))  

    val sumResult = superNum1 + superNum2  
    println(sumResult)
 
    val numberBool1 = new SuperNumber(List(true, false, true))
    val numberBool2 = new SuperNumber(List(true, false, true))
    val check =  numberBool1 + (numberBool2)
    var check2 = numberBool1 | numberBool2
    println(check)  //101 + 101 = 1010
    println(check2)
 
  }
}

```

# Тестирование

Результат запуска программы:

```
5 310606443 8 10
true false true false
true false true
```

# Вывод

 В реализации данной лабораторной работы были приобретены навыки разработки обобщённых классов
на языке Scala с использованием неявных преобразований типов. Написано длинное сложение для 
целочисленных типов и типа Boolean.