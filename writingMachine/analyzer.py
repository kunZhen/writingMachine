import sys
from writingMachine.analizadorLexico import analysis, errors_description, lexical_errors
from writingMachine.analizadorSintactico import parse, syntax_errors
from writingMachine.ast.visitor import ASTVisitor


class Analyzer:
    def __init__(self, input_file):
        self.input_file = input_file

    def process_code(self):
        # Leer el contenido del archivo
        try:
            with open(self.input_file, 'r') as file:
                code = file.read()
        except FileNotFoundError:
            print(f"Error: El archivo '{self.input_file}' no se encontró.")
            return

        # Imprimir los tokens encontrados
        print("Tokens encontrados:")
        tokens = analysis(code)  # Asumiendo que tienes una función de análisis léxico llamada `analysis`
        print(tokens)

        # Verificar y mostrar errores léxicos
        if errors_description:
            print("\nErrores lexicos:")
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
        print("\nAST:")
        visitor.print_ast(ast_root)

        # Imprimir la tabla de símbolos
        visitor.print_symbol_table()  # Asegúrate de tener un método para imprimir la tabla de símbolos

        # Verificar errores léxicos y semánticos
        if lexical_errors:
            print("\nErrores lexicos:")
            for error in lexical_errors:
                print(error)

        if visitor.semantic_errors:
            print("\nErrores semanticos:")
            for error in visitor.semantic_errors:
                print(error)

    def generate_log(self, output_log="output_log.txt"):
        # Guardamos la salida estándar original (que va a la consola)
        original_stdout = sys.stdout

        # Redirigir sys.stdout al archivo
        with open(output_log, "w") as f:
            sys.stdout = f
            try:
                # Ejecutamos el procesamiento del código
                self.process_code()
            finally:
                # Restaurar sys.stdout a la consola original
                sys.stdout = original_stdout


if __name__ == '__main__':
    # Crear una instancia de CodeProcessor con el archivo de entrada
    processor = Analyzer("errores_lexicos.txt")

    # Generar el log
    processor.generate_log()
