import os
import subprocess

def setup_antlr_project():
    # Define paths
    grammar_file = 'Champi.g4'
    output_dir = 'generated'
    antlr_jar = 'antlr/antlr4-4.9.3-complete.jar'  # Asegúrate de usar la versión correcta

    # Ensure output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Generate lexer and parser
    subprocess.run([
        'java', '-jar', antlr_jar,
        '-Dlanguage=Python3',
        '-o', output_dir,
        grammar_file
    ])

    print("ANTLR project setup completed.")

if __name__ == '__main__':
    setup_antlr_project()
