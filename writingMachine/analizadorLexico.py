import ply.lex as lex

errors_description = []
lexical_errors = []
first_token_checked = False  # Flag para verificar si ya revisamos el primer token


# Lista de tokens
tokens = (
    'DEF', 'ID', 'NUMBER', 'BOOLEAN', 'LBRACKET',
    'RBRACKET', 'LPAREN', 'RPAREN', 'SEMI', 'COMMA',
    'PLUS', 'MINUS', 'MULT_OP', 'DIV_OP', 'MULT', 'DIV',
    'SUM', 'RANDOM', 'SUBSTR', 'SMALLER', 'GREATER', 'OR',
    'AND', 'EQUAL', 'BEGINNING', 'UP', 'DOWN', 'USECOLOR',
    'POSY', 'POSX', 'POS', 'CONTINUELEFT', 'CONTINUERIGHT',
    'CONTINUEDOWN', 'CONTINUEUP', 'ADD', 'PUT', 'FOR',
    'TO', 'LOOP', 'END', 'CASE', 'WHEN', 'THEN', 'ELSE',
    'REPEAT', 'UNTIL', 'WHILE', 'WHEND', 'EQUALS',
    'LT', 'GT', 'TURNLEFT', 'TURNRIGHT','COMMENT'
)

# Expresiones regulares para los tokens
t_DEF = r'Def'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_SEMI = r';'
t_COMMA = r','
t_EQUALS = r'='
t_LT = r'<'
t_GT = r'>'
t_SUM = r'Sum'
t_MULT = r'Mult'
t_DIV = r'Div'
t_PLUS = r'\+'
t_MINUS = r'-'
t_MULT_OP = r'\*'
t_DIV_OP = r'/'
t_RANDOM = r'Random'
t_SUBSTR = r'Substr'
t_SMALLER = r'Smaller'
t_GREATER = r'Greater'
t_OR = r'Or'
t_AND = r'And'
t_EQUAL = r'Equal'
t_BEGINNING = r'Beginning'
t_UP = r'Up'
t_DOWN = r'Down'
t_USECOLOR = r'UseColor'
t_POSY = r'PosY'
t_POSX = r'PosX'
t_POS = r'Pos'
t_CONTINUELEFT = r'ContinueLeft'
t_CONTINUERIGHT = r'ContinueRight'
t_CONTINUEDOWN = r'ContinueDown'
t_CONTINUEUP = r'ContinueUp'
t_ADD = r'Add'
t_PUT = r'Put'
t_FOR = r'For'
t_TO = r'To'
t_LOOP = r'Loop'
t_END = r'End'
t_CASE = r'Case'
t_WHEN = r'When'
t_THEN = r'Then'
t_ELSE = r'Else'
t_REPEAT = r'Repeat'
t_UNTIL = r'Until'
t_WHILE = r'While'
t_WHEND = r'Whend'
t_TURNLEFT = r'TurnLeft'
t_TURNRIGHT = r'TurnRight'

# Regla para reconocer booleanos
def t_BOOLEAN(t):
    r'TRUE|FALSE|True|False|false|true'
    t.type = 'BOOLEAN'
    return t

# Regla para reconocer numeros
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Regla para reconocer identificadores
def t_ID(t):
    r'[a-zA-Z_@][a-zA-Z_0-9@]*'
    if t.value in ('Mult', 'Div', 'Sum', 'Random', 'Substr', 'Smaller', 'Greater', 'Or', 'And', 'Equal',
                   'Beginning', 'Up', 'Down', 'UseColor', 'PosY', 'PosX', 'Pos', 'ContinueLeft',
                   'ContinueRight', 'ContinueDown', 'ContinueUp', 'Add', 'Put', 'For', 'to', 'Loop', 'End',
                   'Case', 'When', 'Then', 'Else', 'Repeat', 'Until', 'While', 'Whend', 'Def', 'PUT', 'ADD',
                   'case', 'TurnLeft', 'TurnRight'):
        t.type = t.value.upper()  # Cambiar el tipo a MULT, DIV o SUM
    return t

# Ignorar espacios y tabulaciones
t_ignore = ' \t'

# Manejo de saltos de linea
def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_COMMENT(t):
    r'//.*'
    global first_token_checked
    if not first_token_checked:
        first_token_checked = True
        return t  # Retornamos el primer comentario para la verificación
    # Después del primer token, ignoramos los comentarios
    pass
# Manejo de errores lexicos
def t_error(t):
    global lexical_errors, first_token_checked
    if not first_token_checked:
        lexical_errors.append(f"Error Lexico: El programa debe comenzar con un comentario en la línea {t.lineno}")
        first_token_checked = True
    else:
        lexical_errors.append(f"Error Lexico: Simbolo invalido '{t.value[0]}' en la linea {t.lineno}")
    t.lexer.skip(1)


# Construir el lexer
lexer = lex.lex()

# Funcion de analisis lexico
# Funcion de analisis lexico
def analysis(input):
    global first_token_checked
    first_token_checked = False  # Restablecer flag para cada análisis
    lexer.input(input)
    tokens = []

    for tok in lexer:
        if not first_token_checked:
            # Verificar si el primer token no es un comentario
            if tok.type != 'COMMENT':
                lexical_errors.append(
                    f"Error Léxico: El programa debe comenzar con un comentario en la línea {tok.lineno}")
            # Si es comentario o no, marcamos que ya revisamos el primer token
            first_token_checked = True
            # Saltamos el comentario sin agregarlo a la lista de tokens
            if tok.type == 'COMMENT':
                continue

        # Procesar tokens normales (excluyendo el primer comentario)
        if tok.type != 'COMMENT':  # No agregamos ningún comentario a la lista de tokens
            column = tok.lexpos - input.rfind('\n', 0, tok.lexpos)
            tokens.append((tok.value, tok.type, tok.lineno, column))

    return tokens

# Ejemplo de prueba
if __name__ == '__main__':
    code = """
        //vamos
        Def(var1,true)
        //sii
        """
    print("Tokens encontrados:")
    print(analysis(code))

    if lexical_errors:
        print("\nErrores lexicos:")
        for error in lexical_errors:
            print(error)
