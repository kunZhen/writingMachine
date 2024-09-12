from antlr4 import *
from generated.ChampiLexer import ChampiLexer
from generated.ChampiParser import ChampiParser
from ChampiASTListener import ChampiASTListener  # Asegúrate de que la importación sea correcta

def main():
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

    # Creamos el listener
    listener = ChampiASTListener()

    # Creamos el walker para recorrer el árbol con el listener
    walker = ParseTreeWalker()
    walker.walk(listener, tree)

if __name__ == '__main__':
    main()
