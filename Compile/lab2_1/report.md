% Лабораторная работа № 2.1. Синтаксические деревья
% 15 мая 2024 г.
% Ольга Александрова, ИУ9-61Б

# Цель работы
Целью данной работы является изучение представления синтаксических деревьев в памяти компилятора
и приобретение навыков преобразования синтаксических деревьев.

# Индивидуальный вариант
Заменить все умножения и деления на число, являющееся степенью двойки, на соответствующий 
побитовый сдвиг.

# Реализация

Демонстрационная программа:

```go
package main

func main() {
	x := 2 * 4
	y := 16 / 4
	z := 8 * 16 / 2
	w := 64 / 8 / 2
	u := 256 / 16 / 4 / 2
	a := 234 * 31 / 32
}

```

Программа, осуществляющая преобразование синтаксического дерева:

```go
package main

import (
	"fmt"
	"go/ast"
	"go/format"
	"go/parser"
	"go/token"
	"math/bits"
	"os"
	"strconv"
)

func main() {

	if len(os.Args) != 2 {
		return
	}

	fset := token.NewFileSet()
	if file, err := parser.ParseFile(fset, os.Args[1], nil, parser.ParseComments); err == nil {
		transformSyntaxTree(file)

		if format.Node(os.Stdout, fset, file) != nil {
			fmt.Printf("Formatter error: %v\n", err)
		}
	} else {
		fmt.Printf("Errors in %s\n", os.Args[1])
	}
}

func transformSyntaxTree(file *ast.File) {
	ast.Inspect(file, func(node ast.Node) bool {
		switch n := node.(type) {
		case *ast.BinaryExpr:
			if n.Op == token.MUL || n.Op == token.QUO {
				if isPowerOfTwo(n.Y) {
					shiftOp := token.SHL
					if n.Op == token.QUO {
						shiftOp = token.SHR
					}

					shiftExpr := &ast.BinaryExpr{
						X:     n.X,
						Op:    shiftOp,
						Y:     &ast.BasicLit{Value: fmt.Sprintf("%d", getShiftAmount(n.Y))},
						OpPos: n.OpPos,
					}

					*n = *shiftExpr
				}
			}
		}
		return true
	})
}

func isPowerOfTwo(expr ast.Expr) bool {
	if basicLit, ok := expr.(*ast.BasicLit); ok {
		if basicLit.Kind == token.INT {
			value := basicLit.Value
			if value != "0" && value[0] != '-' {
				intValue, err := strconv.Atoi(value)
				if err != nil {
					return false
				}
				return intValue > 0 && (intValue&(intValue-1)) == 0
			}
		}
	}
	return false
}

func getShiftAmount(expr ast.Expr) int64 {
	if basicLit, ok := expr.(*ast.BasicLit); ok {
		if basicLit.Kind == token.INT {
			if intValue, err := strconv.ParseInt(basicLit.Value, 0, 64); err == nil {
				return int64(bits.TrailingZeros64(uint64(intValue)))
			}
		}
	}
	return 0
}

```

# Тестирование

Результат трансформации демонстрационной программы:

```go
func main() {
    x := 2 << 2
    y := 16 >> 2
    z := 8 << 4 >> 1
    w := 64 >> 3 >> 1
    u := 256 >> 4 >> 2 >> 1
    a := 234 * 31 >> 5
}

```


# Вывод

В ходе выполнения данной лабораторной работы были изучены принципы представления синтаксических
деревьев в памяти компилятора и навыки преобразования этих деревьев.

Для удобного изучения синтаксических деревьев используется функция ast.Fprint из пакета "go/ast". 
Эта функция создает листинг синтаксического дерева, что позволяет легко визуализировать его структуру.

В данной лабораторной работе была поставлена задача оптимизации кода путем замены умножений
и делений на число, являющееся степенью двойки, на соответствующий побитовый сдвиг. 
Для решения этой задачи использовались следующие методы из библиотек:

• parser.ParseFile: Для построения синтаксического дерева из исходного кода программы.

• ast.Inspect: Для обхода синтаксического дерева и поиска узлов, представляющих операции умножения и деления.

• format.Node: Для преобразования преобразованного синтаксического дерева обратно в исходный код.

А также написаны собственные методы для решения исходной задачи:

• isPowerOfTwo: Для проверки, является ли число степенью двойки.

• getShiftAmount: Для вычисления количества битов, на которые нужно выполнить сдвиг.

В результате данной лабораторной работы было усовершенствовано понимание структуры синтаксических деревьев,
а также приобретены практические навыки их анализа, преобразования.