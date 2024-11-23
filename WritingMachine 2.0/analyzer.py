import sys
from analizadorLexico import analysis, reset_lexer
from analizadorSintactico import parse, reset_parser
from ast_custom.visitor import ASTVisitor
from llvmlite import ir, binding
import codigo_intermedio


class Analyzer:
    def __init__(self, input_file):
        self.input_file = input_file
        
        # Inicializar LLVM una sola vez
        binding.initialize()
        binding.initialize_native_target()
        binding.initialize_native_asmprinter()

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

        # Código intermedio y generación de código 
        if not hasattr(visitor, 'semantic_errors') or not visitor.semantic_errors:
            try:
                print("\nGenerando código intermedio LLVM:")
                generator = codigo_intermedio.LLVMCodeGenerator()
                
                # Generar código intermedio a partir del AST
                generator.generate_from_ast(ast_root)
                
                # Optimizar
                generator.optimize_module()
                
                # Imprimir el código LLVM IR para debugging
                print("\nCódigo LLVM IR generado:")
                print(str(generator.module))
                
                # Generar código de máquina
                machine_code = generator.generate_machine_code()
                
                # Guardar el código objeto en un archivo
                output_file = self.input_file.replace('.txt', '.o')
                with open(output_file, 'wb') as f:
                    f.write(machine_code)
                print(f"\nCódigo objeto generado en: {output_file}")
                
            except Exception as e:
                print(f"\nError durante la generación de código: {str(e)}")

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