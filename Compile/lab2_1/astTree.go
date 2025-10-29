package main

//go build astTree.go
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

//2- 10
//1 -01
//3 - 11
//4 - 100

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
