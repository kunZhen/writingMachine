import sys
from analizadorLexico import analysis, reset_lexer
from analizadorSintactico import parse, reset_parser
from ast_custom.visitor import ASTVisitor


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

        # Análisis léxico
        print("Tokens encontrados:")
        tokens = analysis(code)
        print(tokens)

        # Verificar errores léxicos
        from analizadorLexico import lexical_errors
        if lexical_errors:
            print("\nErrores lexicos:")
            for error in lexical_errors:
                print(error)

        # Si hay errores léxicos, podríamos querer detener el proceso aquí
        if lexical_errors:
            return

        # Análisis sintáctico
        try:
            ast_root = parse(code)
            print("\nAST:", ast_root)

            from analizadorSintactico import syntax_errors
            if syntax_errors:
                print("\nErrores de sintaxis:")
                for error in syntax_errors:
                    print(error)
        except Exception as e:
            print(f"Error durante el análisis sintáctico: {str(e)}")
            return

        # Si hay errores sintácticos, podríamos querer detener el proceso aquí
        if syntax_errors:
            return

        # Análisis semántico
        try:
            visitor = ASTVisitor()
            visitor.visit(ast_root)
            print("\nAST:")
            visitor.print_ast(ast_root)
            visitor.print_symbol_table()

            if hasattr(visitor, 'semantic_errors') and visitor.semantic_errors:
                print("\nErrores semanticos:")
                for error in visitor.semantic_errors:
                    print(error)
        except Exception as e:
            print(f"Error durante el análisis semántico: {str(e)}")

    def generate_log(self, output_log="output_log.txt"):
        original_stdout = sys.stdout
        try:
            with open(output_log, "w") as f:
                sys.stdout = f
                self.process_code()
        finally:
            sys.stdout = original_stdout


if __name__ == '__main__':
    processor = Analyzer("errores_lexicos.txt")
    processor.generate_log()