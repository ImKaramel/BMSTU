def kadane(arr: List[Int]): (Int, Int) = {
    if (arr.isEmpty) {
        return (-1, -1)
    }
    
    def kadaneHelper(lst: List[Int], maxSoFar: Int, maxEndingHere: Int, currStart: Int, 
            maxStart: Int, maxEnd: Int, index: Int): (Int, Int) = {
        lst match {
            case Nil => (maxStart, maxEnd)
            case x :: xs =>
                val newMaxEndingHere = maxEndingHere + x
                val newMaxSoFar = if (maxSoFar < newMaxEndingHere) newMaxEndingHere else maxSoFar
                val (newMaxStart, newMaxEnd) = if (newMaxEndingHere > maxSoFar) (currStart, index) 
                    else (maxStart, maxEnd)
                
                if (newMaxEndingHere < 0) {
                    kadaneHelper(xs, newMaxSoFar, 0, index + 1,  newMaxStart, newMaxEnd, index + 1)
                } else {
                    kadaneHelper(xs, newMaxSoFar, newMaxEndingHere, currStart, 
                                    newMaxStart, newMaxEnd, index + 1)
                }
        }
    }
    
    kadaneHelper(arr, Int.MinValue, 0, 0, 0, 0, 0)
}

// kadane(List(-2, 1, -3, 4, -1, 2, 1, -5, 4)) //(3,6)
// kadane(List(1, 2, 3, 4, 5)) //(0,4)
// kadane(List(-10, -2, 99, -4, -5)) //(2,2)
// kadane(List())

// pandoc \
//   --pdf-engine=xelatex \
//   -V 'mainfont:Liberation Serif' \
//   -V 'monofont:Liberation Mono' \
//   report.md -o out.pdf
 