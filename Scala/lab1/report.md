% Лабораторная работа № 1 «Введение в функциональное
  программирование на языке Scala»
% 14 марта 2024 г.
% Ольга Александрова, ИУ9-61Б

# Цель работы

Целью данной работы является ознакомление с программированием на языке Scala на основе чистых функций.

# Индивидуальный вариант

Функция kadane: List[Int] => (Int, Int), выполняющая поиск границ подпоследовательности с максимальной суммой 
(алгоритм Кадана).

# Реализация и тестирование

Работа в REPL-интерпретаторе Scala:

```scala
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
```

# Тестовые данные
1) Пример

```kadane(List(-2, 1, -3, 4, -1, 2, 1, -5, 4))```

Вывод - ```(3,6)```

2) Пример

kadane(List(1, 2, 3, 4, 5))

Вывод - ```(3,6)```

# Вывод

В данной лабораторной работе был получен опыт работы с REPL-интерпретатором языка Scala. 
В ходе реализации задания я ознакомилась с функциональной парадигмой даннного языка программирования и изучила
алгоритм поиска максимальной подпоследовательности (Алгоритм Кадана).