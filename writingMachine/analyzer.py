import sys

from writingMachine.analizadorLexico import analysis, errors_description, lexical_errors
from writingMachine.analizadorSintactico import parse, syntax_errors
from writingMachine.ast.visitor import ASTVisitor


def main():

    input_file = "errores_sintacticos.txt"  # Nombre del archivo de código

    # Leer el contenido del archivo
    try:
        with open(input_file, 'r') as file:
            code = file.read()
    except FileNotFoundError:
        print(f"Error: El archivo '{input_file}' no se encontró.")
        return

    # Imprimir los tokens encontrados
    print("Tokens encontrados:")
    tokens = analysis(code)  # Asumiendo que tienes una función de análisis léxico llamada `analysis`
    print(tokens)

    # Verificar y mostrar errores léxicos
    if errors_description:
        print("\nErrores léxicos:")
        for error in errors_description:
            print(error)

    # Analizar el código y obtener el AST
    ast_root = parse(code)  # Asumiendo que tienes una función de análisis sintáctico llamada `parse`
    print("\nAST:", ast_root)  # Para verificar que se construyó correctamente


    if syntax_errors:
        print("\nErrores de sintaxis:")
        for error in syntax_errors:
            print(error)

    # Crear un visitor para ejecutar el AST
    visitor = ASTVisitor()  # Usa tu clase de visitor
    visitor.visit(ast_root)  # Ejecuta el árbol AST
    visitor.print_ast(ast_root);
    # Imprimir la tabla de símbolos
    visitor.print_symbol_table()  # Asegúrate de tener un método para imprimir la tabla de símbolos

    if lexical_errors:
        print("\nErrores léxicos:")
        for error in lexical_errors:
            print(error)
    if visitor.semantic_errors:
        print("\nErrores semánticos:")
        for error in visitor.semantic_errors:
            print(error)

if __name__ == '__main__':
    main()
