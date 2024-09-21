import ply.lex as lex

# Listas para almacenar errores
errors_description = []

# Lista de tokens
tokens = (
    'DEF',          # Palabra clave Def
    'ID',           # Identificadores (nombre_variable)
    'NUMBER',       # Números (valor)
    'BOOLEAN',      # Booleanos (TRUE o FALSE)
    'LPAREN',       # Paréntesis izquierdo '('
    'RPAREN',       # Paréntesis derecho ')'
    'SEMI',         # Punto y coma ';'
    'COMMA',        # Coma ','
)

# Expresiones regulares para los tokens
t_DEF = r'Def'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_SEMI = r';'
t_COMMA = r','

# Regla para reconocer booleanos (BOOLEAN)
def t_BOOLEAN(t):
    r'TRUE|FALSE'
    return t
# Regla para reconocer identificadores (ID)
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    return t

# Regla para reconocer números (NUMBER)
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)  # Convertir el valor a entero
    return t

# Ignorar espacios y tabulaciones
t_ignore = ' \t'

# Manejo de saltos de línea
def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Manejo de errores léxicos
def t_error(t):
    global errors_description
    errors_description.append(f"Not valid symbol '{t.value[0]}' en la linea {t.lineno}")
    t.lexer.skip(1)  # Saltar el carácter no válido

# Construir el lexer
lexer = lex.lex()

# Función de análisis léxico
def analysis(input):
    lexer.input(input)
    tokens = []

    for tok in lexer:
        column = tok.lexpos - input.rfind('\n', 0, tok.lexpos)  # Calcular la columna
        tokens.append((tok.value, tok.type, tok.lineno, column))
    return tokens

# Ejemplo de prueba
if __name__ == '__main__':
    code = "Def(variable1, FALSE);"
    print("Tokens encontrados:")
    print(analysis(code))

    if errors_description:
        print("\nErrores léxicos:")
        for error in errors_description:
            print(error)
