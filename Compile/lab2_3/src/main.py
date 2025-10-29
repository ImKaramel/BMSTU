from src.parser import Parser
from src.scanner import Compiler

kIndent = "\t\t"
def main():

    filePath = "in.txt"
    with open(filePath, 'r') as file:
        reader = file.read()

    compiler = Compiler()
    scn = compiler.GetScanner(reader)

    parser = Parser()

    root = parser.TopDownParse(scn)
    print(root.Output(kIndent))


if __name__ == "__main__":
    main()