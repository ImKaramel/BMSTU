
class BinaryNumber private (private val value: BigInt) {

    def getValue: BigInt = value

    def +(other: BinaryNumber): BinaryNumber = {
        val binary1 = this.value.toString(2).reverse
        val binary2 = other.value.toString(2).reverse

        val maxLength = binary1.length max binary2.length
        val num1 = binary1.padTo(maxLength, '0')
        val num2 = binary2.padTo(maxLength, '0')

        var carry = '0'
        val result = num1.zip(num2).map { case (bit1, bit2) =>
        val sum = (bit1.asDigit + bit2.asDigit + carry.asDigit) % 2
        carry = if ((bit1.asDigit + bit2.asDigit + carry.asDigit) >= 2) '1' else '0'
        sum.toString.head
        }.reverse.mkString

        val finalResult =
        if (carry == '1') 
            BinaryNumber(BigInt("1" + result, 2))
        else 
            BinaryNumber(BigInt(result, 2))

        finalResult
    }

    def  *(other: BinaryNumber): BinaryNumber = {
        val num1 = this.value.toString(2).reverse
        val num2 = other.value.toString(2).reverse

        var results: List[String] = List.empty
        var zeroPadding = 0

        for (digit <- num1) {
            var result: String = ""
            var carry = 0

            if (digit == '0') {
                zeroPadding += 1
            } else {
                for (bit <- num2) {
                    val multiply = (digit.asDigit * bit.asDigit + carry) % 2
                    result = multiply.toString + result
                }
                result = result + "0" * zeroPadding
                zeroPadding += 1
                results = result :: results
            }
        }

    
        val binaryResults = results.map(s => BinaryNumber(BigInt(s, 2)))

        val finalResult = binaryResults.reduce((acc, curr) => acc+curr)

        finalResult
    }
}

object BinaryNumber {
  def apply(value: BigInt): BinaryNumber = {
    require(value >= BigInt(0), "Должно быть неотрицательное число")
    new BinaryNumber(value)
  }
}

object Main {
  def main(args: Array[String]): Unit = {
    val num1 = BinaryNumber(BigInt("10101", 2))
    val num2 = BinaryNumber(BigInt("100", 2))

    val sum = num1+num2
    val mul = num1*num2

    println(s"Поразрядная сумма: ${sum.getValue.toString(2)}")
    println(s"Поразрядное произведение: ${mul.getValue.toString(2)}")
  }
}
 