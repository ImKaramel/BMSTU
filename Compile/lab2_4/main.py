from parser import Parser
from scanner import Compiler


def main():

    filePath = "/Users/assistentka_professora/Desktop/Compile/lab2_4/in.txt"
    with open(filePath, 'r') as file:
        reader = file.read()

    compiler = Compiler()

    scn = compiler.GetScanner(reader)
    parser = Parser(scn)

    p = parser.program()
    p.Print("")

if __name__ == "__main__":
    main()
