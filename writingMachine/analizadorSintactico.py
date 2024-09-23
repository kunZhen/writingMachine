import random

import ply.yacc as yacc
from analizadorLexico import tokens
# Jerarquia de palabras
precedence = (
    ('left', 'OR'),        # Operador OR
    ('left', 'AND'),       # Operador AND
    ('left', 'EQUAL', 'SMALLER', 'GREATER', 'EQUALS',
     'LT', 'GT'),  # Comparaciones
    ('left', 'PLUS', 'MINUS', 'SUM', 'SUBSTR'),   # Suma y resta
    ('left', 'MULT_OP', 'DIV_OP', 'MULT', 'DIV'),  # Multiplicación y división
)
# Variables necesarias
variables = {}
x_position = 1  # Posición inicial en el eje x
y_position = 1  # Posición inicial en el eje y
current_color = 1  # 1: Negro, 2: Rojo

# Regla inicial (punto de entrada)
def p_program(p):
    '''program : statement
               | program statement'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

# produccion statment para casos de control
def p_statement(p):
    '''statement : expression SEMI
                 | expression
                 | for_statement SEMI
                 | case_statement SEMI
                 | repeat_statement SEMI
                 | while_statement SEMI'''
    p[0] = p[1]

# Reglas para las expresiones aritméticas
def p_expression_binop(p):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression MULT_OP expression
                  | expression DIV_OP expression'''
    if p[2] == '+':
        p[0] = p[1] + p[3]
    elif p[2] == '-':
        p[0] = p[1] - p[3]
    elif p[2] == '*':
        p[0] = p[1] * p[3]
    elif p[2] == '/':
        if p[3] == 0:
            print("Error: División por cero")
            p[0] = None
        else:
            p[0] = p[1] / p[3]

# Reglas para expresiones de comparacion
def p_expression_comparison(p):
    '''expression : expression LT expression
                  | expression GT expression
                  | expression EQUALS expression'''
    if p[2] == '<':
        p[0] = p[1] < p[3]
    elif p[2] == '>':
        p[0] = p[1] > p[3]
    elif p[2] == '=':
        p[0] = p[1] == p[3]

# Regla para definir variable
def p_def_statement(p):
    '''expression : DEF LPAREN ID COMMA expression RPAREN'''
    if p[3] in variables:
        print(f"Error: La variable '{p[3]}' ya está definida.")
    else:
        variables[p[3]] = p[5]  # Almacena la variable con su valor
        p[0] = f"Definido {p[3]} = {p[5]}"

# Regla para modificar variable
def p_put_statement(p):
    '''expression : PUT LPAREN ID COMMA expression RPAREN'''
    if p[3] in variables:
        variables[p[3]] = p[5]  # Actualiza la variable existente
        p[0] = f"Actualizado {p[3]} = {p[5]}"
    else:
        print(f"Error: Variable '{p[3]}' no definida")

# Regla para la funcion ADD
def p_add_statement(p):
    '''expression : ADD LPAREN ID RPAREN
                     | ADD LPAREN ID COMMA expression RPAREN'''

    if p[3] not in variables:
        print(f"Error: '{p[3]}' no es una variable válida.")
        p[0] = None
    else:
        # Caso 1: Un solo identificador
        if len(p) == 5:
            variables[p[3]] += 1
            p[0] = f"Incrementado {p[3]} a {variables[p[3]]}"

        # Caso 2: Identificador y un valor
        elif len(p) == 7:
            increment_value = p[5]  # Valor de incremento

            # Verifica si el valor es una variable
            if isinstance(increment_value, str) and increment_value in variables:
                increment_value = variables[increment_value]  # Recupera el valor de la variable
            else:
                if isinstance(increment_value, (int, float)):
                    increment_value = increment_value
                else:
                    print(f"Error: El incremento debe ser un número o una variable.")
                    p[0] = None
                    return

            variables[p[3]] += increment_value
            p[0] = f"Incrementado {p[3]} en {increment_value} a {variables[p[3]]}"

# Regla para la funcion ContinueUp
def p_continueup_statement(p):
    '''expression : CONTINUEUP LPAREN expression RPAREN SEMI'''

    # Obtiene el valor de n (puede ser un número, operación o variable)
    move_units = p[3]

    if isinstance(move_units, (int, float)):  # Verifica si es un número válido
        global y_position
        y_position += move_units  # Incrementa la posición en el eje y
        p[0] = f"Movido {move_units} unidades hacia arriba. Nueva posición en Y: {y_position}"
    else:
        print(f"Error: No se puede mover {move_units} unidades. Verifica el valor.")
        p[0] = None

# Regla para la funcion ContinueDown
def p_continuedown_statement(p):
    '''expression : CONTINUEDOWN LPAREN expression RPAREN SEMI'''

    # Obtiene el valor de n (puede ser un número, operación o variable)
    move_units = p[3]

    if isinstance(move_units, (int, float)):  # Verifica si es un número válido
        global y_position
        y_position -= move_units  # Decrementa la posición en el eje y
        p[0] = f"Movido {move_units} unidades hacia abajo. Nueva posición en Y: {y_position}"
    else:
        print(f"Error: No se puede mover {move_units} unidades. Verifica el valor.")
        p[0] = None

# Regla para la funcion ContinueRight
def p_continueright_statement(p):
    '''expression : CONTINUERIGHT LPAREN expression RPAREN SEMI'''

    # Obtiene el valor de n (puede ser un número, operación o variable)
    move_units = p[3]

    if isinstance(move_units, (int, float)):  # Verifica si es un número válido
        global x_position
        x_position += move_units  # Incrementa la posición en el eje x
        p[0] = f"Movido {move_units} unidades hacia derecha. Nueva posición en X: {x_position}"
    else:
        print(f"Error: No se puede mover {move_units} unidades. Verifica el valor.")
        p[0] = None

# Regla para la funcion ContinueLeft
def p_continueleft_statement(p):
    '''expression : CONTINUELEFT LPAREN expression RPAREN SEMI'''

    # Obtiene el valor de n (puede ser un número, operación o variable)
    move_units = p[3]

    if isinstance(move_units, (int, float)):  # Verifica si es un número válido
        global x_position
        x_position -= move_units  # Incrementa la posición en el eje x
        p[0] = f"Movido {move_units} unidades hacia izquierda. Nueva posición en X: {x_position}"
    else:
        print(f"Error: No se puede mover {move_units} unidades. Verifica el valor.")
        p[0] = None

# Regla que modifica la posicion del lapiz
def p_pos_statement(p):
    '''expression : POS LPAREN expression COMMA expression RPAREN'''
    global x_position, y_position

    x_val = p[3]  # Resuelve el valor de X
    y_val = p[5]  # Resuelve el valor de Y

    # Verifica si X es una variable o una constante
    if isinstance(x_val, str) and x_val in variables:
        x_position = variables[x_val]  # Valor de la variable X
    else:
        x_position = x_val  # Constante numérica o expresión resuelta

    # Verifica si Y es una variable o una constante
    if isinstance(y_val, str) and y_val in variables:
        y_position = variables[y_val]  # Valor de la variable Y
    else:
        y_position = y_val  # Constante numérica o expresión resuelta

    # Actualiza y muestra la posición actual en X e Y
    p[0] = f"Posición actualizada a X: {x_position}, Y: {y_position}"
    print(p[0])  # Muestra la posición actualizada

# Regla que modifica solamente la posicion X
def p_posx_statement(p):
    '''expression : POSX expression'''
    global x_position

    x_val = p[2]  # Resuelve el valor de X

    # Verifica si X es una variable o una constante
    if isinstance(x_val, str) and x_val in variables:
        x_position = variables[x_val]  # Valor de la variable X
    else:
        x_position = x_val  # Constante numérica o expresión resuelta

    # Actualiza solo la posición X y respeta Y
    p[0] = f"Posición actualizada a X: {x_position}, Y: {y_position}"

# Regla que modifica solamente la posicion Y
def p_posy_statement(p):
    '''expression : POSY expression'''
    global y_position

    y_val = p[2]  # Resuelve el valor de X

    # Verifica si Y es una variable o una constante
    if isinstance(y_val, str) and y_val in variables:
        y_position = variables[y_val]  # Valor de la variable X
    else:
        y_position = y_val  # Constante numérica o expresión resuelta

    # Actualiza solo la posición Y y respeta X
    p[0] = f"Posición actualizada a X: {x_position}, Y: {y_position}"

# Regla que modifica el color
def p_usecolor_statement(p):
    '''expression : USECOLOR expression'''
    global current_color

    color_value = p[2]  # Resuelve el valor del color (1 o 2)

    # Verifica si el valor es 1 o 2
    if color_value == 1 or color_value == 2:
        current_color = color_value
        color_name = "Negro" if color_value == 1 else "Rojo"
        p[0] = f"Color cambiado a {color_name} (Compartimiento {current_color})"
    else:
        # Generar un error si el valor no es 1 ni 2
        p[0] = f"Error: {color_value} no es un color válido. Usa 1 (Negro) o 2 (Rojo)."

# Regla que baja el lapiz
def p_down_statement(p):
    '''expression : DOWN'''
    global pen_down
    pen_down = True
    p[0] = "Lapicero colocado en la superficie (Down)"

# Regla que sube el lapiz
def p_up_statement(p):
    '''expression : UP'''
    global pen_down
    pen_down = False
    p[0] = "Lapicero levantado de la superficie (Up)"

# Regla que mueve a la posicion 1,1 el lapiz
def p_beginning_statement(p):
    '''expression : BEGINNING'''
    global x_position, y_position
    x_position = 1
    y_position = 1
    p[0] = f"Lapicero colocado en la posición inicial: X: {x_position}, Y: {y_position}"

# Regla que compara si dos expresiones son iguales
def p_equal_statement(p):
    '''expression : EQUAL LPAREN expression COMMA expression RPAREN'''
    n1 = p[3]  # Primer valor a comparar
    n2 = p[5]  # Segundo valor a comparar

    # Compara N1 y N2
    if n1 == n2:
        p[0] = True
    else:
        p[0] = False

# Regla AND
def p_and_statement(p):
    '''expression : AND LPAREN expression COMMA expression RPAREN'''
    n1 = p[3]  # Primera condición
    n2 = p[5]  # Segunda condición

    # Devuelve TRUE si ambas condiciones son verdaderas
    p[0] = bool(n1) and bool(n2)

# Regla OR
def p_or_statement(p):
    '''expression : OR LPAREN expression COMMA expression RPAREN'''
    n1 = p[3]  # Primera condición
    n2 = p[5]  # Segunda condición

    # Devuelve TRUE si ambas condiciones son verdaderas
    p[0] = bool(n1) or bool(n2)

# Regla mayor que
def p_greater_statement(p):
    '''expression : GREATER LPAREN expression COMMA expression RPAREN'''
    n1 = p[3]  # Primer valor
    n2 = p[5]  # Segundo valor

    # Devuelve True si n1 es mayor que n2
    p[0] = n1 > n2

# Regla menor que
def p_smaller_statement(p):
    '''expression : SMALLER LPAREN expression COMMA expression RPAREN'''
    n1 = p[3]  # Primer valor
    n2 = p[5]  # Segundo valor

    # Devuelve True si n1 es menor que n2
    p[0] = n1 < n2

# Regla para la funcion Substr
def p_substr_statement(p):
    '''expression : SUBSTR LPAREN expression COMMA expression RPAREN'''
    n1 = p[3]  # Primer valor (N1)
    n2 = p[5]  # Segundo valor (N2)

    # Verifica que n1 sea mayor o igual que n2
    if n1 < n2:
        print("Error: N1 debe ser mayor o igual que N2.")
        p[0] = None  # Indica que la operación falló
    else:
        p[0] = n1 - n2  # Devuelve el resultado de la resta

# Regla para la funcion random
def p_random_statement(p):
    '''expression : RANDOM LPAREN expression RPAREN'''
    n = p[3]  # Valor de n

    # Generar un número aleatorio entre 0 y n
    if n < 0:
        print("Error: n debe ser un valor no negativo.")
        p[0] = None  # Indica que la operación falló
    else:
        p[0] = random.randint(0, n)  # Genera un número aleatorio

# Regla para la funcion Mult
def p_mult_statement(p):
    '''expression : MULT LPAREN expression COMMA expression RPAREN'''
    n1 = p[3]  # Valor de N1
    n2 = p[5]  # Valor de N2

    # Realiza la multiplicación y asigna el resultado
    p[0] = n1 * n2  # Retorna el resultado de la multiplicación

# Regla para la funcion Div
def p_div_statement(p):
    '''expression : DIV LPAREN expression COMMA expression RPAREN'''
    n1 = p[3]  # Valor de N1
    n2 = p[5]  # Valor de N2

    # Verifica que N2 no sea cero para evitar división por cero
    if n2 == 0:
        raise ValueError("Error: División por cero no permitida.")

    # Realiza la división truncando el resultado a un entero
    p[0] = n1 // n2  # Utiliza la división entera

# Regla para la funcion Sum
def p_sum_statement(p):
    '''expression : SUM LPAREN expression COMMA expression RPAREN'''
    n1 = p[3]  # Valor de N1
    n2 = p[5]  # Valor de N2

    # Realiza la suma
    p[0] = n1 + n2  # Suma N1 y N2

# Regla para las expresiones booleanas
def p_expression_boolean(p):
    'expression : BOOLEAN'
    p[0] = p[1].lower() == 'true'

# Regla para las producciones entre parentesis
def p_expression_group(p):
    'expression : LPAREN expression_list RPAREN '
    p[0] = p[2]

# Regla para las producciones entre parentesis cuadrados
def p_expression_bracket(p):
    '''expression_bracket : LBRACKET expression_list SEMI RBRACKET
                  | LBRACKET expression_list RBRACKET'''
    p[0] = p[2]  # Maneja lo que esté dentro de los corchetes

# Regla para la pluralizacion de expresiones
def p_expression_list(p):
    '''expression_list : statement
                      | expression_list SEMI statement'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]
# Regla para la manejar numeros
def p_expression_number(p):
    'expression : NUMBER'
    p[0] = p[1]
# Regla para manejar identificadores
def p_expression_id(p):
    'expression : ID'
    p[0] = variables.get(p[1], 0)  # Retorna 0 si la variable no está definida

# Regla para la definicion del control for
def p_for_statement(p):
    '''for_statement : FOR ID LPAREN NUMBER TO NUMBER RPAREN LOOP expression_bracket END LOOP'''
    var_name = p[2]
    min_val = p[4]
    max_val = p[6]
    body = p[9]

    if var_name in variables:
        print(f"Error: La variable '{var_name}' ya está definida. Usa un nombre diferente para el contador.")
        p[0] = None
        return

    if max_val <= min_val:
        print(f"Error: El valor máximo ({max_val}) debe ser mayor que el valor mínimo ({min_val}).")
        p[0] = None
        return

    results = []
    for i in range(min_val, max_val + 1):
        variables[var_name] = i
        result = execute_statement(body)
        results.append(result)

    del variables[var_name]  # Elimina la variable de control después del bucle
    p[0] = f"For {var_name} from {min_val} to {max_val}: {results}"

# Regla para la ejecucion del for en un futuro
def execute_statement(statement):
    return str(statement)

# Regla para el control case
def p_case_statement(p):
    '''case_statement : CASE ID WHEN NUMBER THEN case_list ELSE case_list END CASE
                      | CASE ID WHEN BOOLEAN THEN case_list ELSE case_list END CASE
                      | CASE ID WHEN NUMBER THEN case_list END CASE
                      | CASE ID WHEN BOOLEAN THEN case_list END CASE'''
    variable = p[2]  # ID es la variable
    if variable not in variables:
        raise ValueError(f"Error: Variable '{variable}' no está definida.")

    if len(p) == 9:  # Caso sin ELSE
        p[0] = f"Case {p[2]} when {p[4]}: {p[6]}"
    elif len(p) == 11:  # Caso con ELSE
        p[0] = f"Case {p[2]} when {p[4]}: {p[6]} else: {p[8]}"

# Regla para el control repeat
def p_repeat_statement(p):
    '''repeat_statement : REPEAT expression_bracket UNTIL expression_bracket'''
    p[0] = f"Repeat: {', '.join(map(str, p[2]))} until {p[4]}"

# Regla para el control While
def p_while_statement(p):
    '''while_statement : WHILE expression_bracket expression_bracket WHEND'''
    # p[2] es la condición del while, p[3] es el bloque de código que se ejecutará
    p[0] = f"While {p[2]}: {p[3]}"

# Regla para pluralizar casos
def p_case_list(p):
    '''case_list : expression_bracket
                 | expression_bracket WHEN NUMBER THEN expression_bracket
                 | expression_bracket WHEN BOOLEAN THEN expression_bracket'''
    if len(p) == 2:
        p[0] = [p[1]]  # Solo una declaración
    else:
        p[0] = [p[1]] + p[3:]  # Agrega la declaración y continúa

# Regla para manejo de errores
def p_error(p):
    if p:
        print(f"Error de sintaxis: símbolo inesperado '{p.value}' en la línea {p.lineno}")
    else:
        print(f"Error de sintaxis: Se esperaba más input pero no se encontró.")

# Construir el parser
parser = yacc.yacc()

# Función para realizar el análisis sintáctico
def parse(input_string):
    return parser.parse(input_string, tracking=True)

# Ejemplo de prueba
if __name__ == "__main__":
    code = "Def(var,2)\n" \
           "Case var\n" \
           "When 1 Then\n" \
           "[For var2(3 to 5) Loop" \
           "[Add(var)] End Loop;]\n" \
           "When 2 Then\n" \
           "[Up;]\n" \
           "Else\n" \
           "[Down;]\n" \
           "End Case;\n"
    result = parse(code)
    print("Resultado:", result)
