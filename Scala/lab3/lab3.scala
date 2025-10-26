import scala.language.implicitConversions

// trait Norm[T] {
//   def normalize(list1: List[T], list2: List[T]): (List[T], List[T])
// }

// implicit object BooleanNorm extends Norm[Boolean] {
//   def normalize(list1: List[Boolean], list2: List[Boolean]): (List[Int], List[Int]) = {
//     val maxLength = list1.length max list2.length
//     val normdList1 = list1.reverse.padTo(maxLength, false).reverse.map(bool => if (bool) 1 else 0)
//     val normdList2 = list2.reverse.padTo(maxLength, false).reverse.map(bool => if (bool) 1 else 0)
//     (normdList1, normdList2)
//   }
// }
 
// implicit def numericNorm[T : Numeric]: Norm[T] = new Norm[T] {
//   def normalize(list1: List[T], list2: List[T]): (List[T], List[T]) = {
//     val maxLength = list1.length max list2.length
//     val normdList1 = list1.reverse.padTo(maxLength, Numeric[T].zero).reverse
//     val normdList2 = list2.reverse.padTo(maxLength, Numeric[T].zero).reverse
//     (normdList1, normdList2)
//   }
// } 

class SuperNumber[T](digits: List[T]) {
  def length: Int = digits.length
  def getDigits: List[T] = digits
  override def toString: String = digits.mkString(" ")

 
  private def normalBool[T](list1: List[T], list2: List[T]): (List[Boolean], List[Boolean]) = {
    val maxLength = list1.length max list2.length
    val normdList1 = list1.reverse.padTo(maxLength, false).reverse
    val normdList2 = list2.reverse.padTo(maxLength, false).reverse
    (normdList1.map(_.asInstanceOf[Boolean]), normdList2.map(_.asInstanceOf[Boolean]))
  }

//   private def normalNum[T](list1: List[T], list2: List[T]): (List[Numeric[T]], List[Numeric[T]]) = {
//     val maxLength = digits.length max other.getDigits.length


//     val maxLength = list1.length max list2.length
//     val normdList1 = list1.reverse.padTo(maxLength, false).reverse
//     val normdList2 = list2.reverse.padTo(maxLength, false).reverse
//     (normdList1.map(_.asInstanceOf[Boolean]), normdList2.map(_.asInstanceOf[Boolean]))
//   }

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

//   def +(other: SuperNumber[T])(implicit num: Numeric[T], boolConv: Boolean => T): SuperNumber[T] = {
  def +(other: SuperNumber[T]): SuperNumber[T] = {
    val binary1 = this.getDigits.mkString("").reverse

    val binary2 = other.getDigits.mkString("").reverse

    val maxLength = binary1.length max binary2.length
    val num1 = binary1.padTo(maxLength, '0')
    val num2 = binary2.padTo(maxLength, '0')

    var carry = '0'
    val result = num1.zip(num2).map { case (bit1, bit2) =>
      val sum = (bit1.asDigit + bit2.asDigit + carry.asDigit) % 2
      carry = if ((bit1.asDigit + bit2.asDigit + carry.asDigit) >= 2) '1' else '0'
      if (sum == 1) true else false
    }.reverse

    if (carry == '1') {
        new SuperNumber[Boolean]((true +: result).toList)
    } else {
    new SuperNumber[Boolean](result.toList)
    }       
  }

}

object SuperNumberNorm {

    implicit def boolNorm(implicit boolList: List[Boolean]): List[Int] = {
        // 2 +: boolList.map(bool => if (bool) 1 else 0)
    }
    implicit def num_ops[T](implicit num: List[Numeric[T]]): SuperNumberNorm[T] =
        new SuperNumberOps[T] {
            def add(a: T, b: T): T = num.plus(a, b)
    }


//     implicit def toInt (numericList: List[Int]): List[Int] = {
//         10 +: numericList.map(_.intValue())
//     }
//     implicit def toLong (numericList: List[Long]): List[Long] = {
//         10 +: numericList 
//   }
}
 

  def +(other: SuperNumber[T])(implicit ev: Numeric[T]): SuperNumber[T] = {
    val num = ev
    val maxLength = digits.length max other.getDigits.length

    val normalizedList1 = digits.reverse.padTo(maxLength, ev.zero).reverse
    val normalizedList2 = other.getDigits.reverse.padTo(maxLength, ev.zero).reverse

    var carry = num.zero
    val result = normalizedList1.zip(normalizedList2).map {
      case (num1, num2) =>
        val sum = num.plus(num.plus(num1, num2), carry)
        carry = num.fromInt(num.toInt(sum) / 10)
        num.fromInt(num.toInt(sum) % 10)
    }
    if (carry != num.zero) {
      new SuperNumber(num.fromInt(0) :: result)
    } else {
      new SuperNumber(result)
    }
  }



object Main {
 
  def main(args: Array[String]): Unit = {
    val numberInt1 = new SuperNumber(List(2, 9, 3))
    val numberInt2 = new SuperNumber(List(4, 5))
    val numberBool1 = new SuperNumber(List(true, false, true))
    val numberBool2 = new SuperNumber(List(true, false, true))
    val check =  numberBool1 + numberBool2
    println(check)  //101 + 01 = 110
    // val num1 = new SuperNumber[Boolean](List(true, false, true))  
    // val num2 = new SuperNumber[Boolean](List(true, true, true)) 
    // val result = num1.+{new SuperNumber[Boolean](num2.getDigits)}



    // println(result)

 
  }
}