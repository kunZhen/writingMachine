from antlr4 import *
from generated.ChampiLexer import ChampiLexer
from generated.ChampiParser import ChampiParser

def main():
    # Cambia 'input_file.txt' por el nombre de tu archivo de texto
    input_file = 'test.txt'

    # Abre el archivo y lee su contenido
    with open(input_file, 'r') as file:
        input_text = file.read()

    # Crea un InputStream a partir del texto leído
    input_stream = InputStream(input_text)
    lexer = ChampiLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = ChampiParser(token_stream)
    tree = parser.program()
    print(tree.toStringTree(recog=parser))

if __name__ == '__main__':
    main()
