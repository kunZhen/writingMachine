import random

import ply.yacc as yacc
from analizadorLexico import tokens
from writingMachine.ast.expression_list import ExpressionList
from writingMachine.ast.substr_statement import SubstrStatement
from writingMachine.ast.add_statement import AddStatement
from writingMachine.ast.and_statement import AndStatement
from writingMachine.ast.beginning_statement import BeginningStatement
from writingMachine.ast.binary_operation import BinaryOperation
from writingMachine.ast.boolean_expression import BooleanExpression
from writingMachine.ast.continuedown_statement import ContinueDownStatement
from writingMachine.ast.continueleft_statement import ContinueLeftStatement
from writingMachine.ast.continueright_statement import ContinueRightStatement
from writingMachine.ast.continueup_statement import ContinueUpStatement
from writingMachine.ast.def_statement import DefStatement
from writingMachine.ast.div_statement import DivStatement
from writingMachine.ast.down_statement import DownStatement
from writingMachine.ast.equal_statement import EqualStatement
from writingMachine.ast.execute_statement import ExecuteStatement
from writingMachine.ast.expression import Expression
from writingMachine.ast.expression_bracket import ExpressionBracket
from writingMachine.ast.expression_group import ExpressionGroup
from writingMachine.ast.for_statement import ForStatement
from writingMachine.ast.greater_statement import GreaterStatement
from writingMachine.ast.id_expression import IdExpression
from writingMachine.ast.mult_statement import MultStatement
from writingMachine.ast.number_expression import NumberExpression
from writingMachine.ast.or_statement import OrStatement
from writingMachine.ast.pos_statement import PosStatement
from writingMachine.ast.posx_statement import PosXStatement
from writingMachine.ast.posy_statement import PosYStatement
from writingMachine.ast.program import Program
from writingMachine.ast.put_statement import PutStatement
from writingMachine.ast.random_statement import RandomStatement
from writingMachine.ast.smaller_statement import SmallerStatement
from writingMachine.ast.sum_statement import SumStatement
from writingMachine.ast.up_statement import UpStatement
from writingMachine.ast.usecolor_statement import UseColorStatement
from writingMachine.ast.visitor import ASTVisitor


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
    '''program : statement SEMI
               | statement
               | program statement SEMI
               | program statement'''
    if len(p) == 2:
        p[0] = Program([p[1]])  # Crea un nodo Program con una lista que contiene un statement
    else:
        p[0] = Program(p[1].statements + [p[2]])  # Crea un nodo Program con la lista de statements

# produccion statment para casos de control
def p_statement(p):
    '''statement : expression
                 | def_statement
                 | put_statement
                 | add_statement
                 | continueup_statement
                 | continuedown_statement
                 | continueright_statement
                 | continueleft_statement
                 | pos_statement
                 | posx_statement
                 | posy_statement
                 | usecolor_statement
                 | down_statement
                 | up_statement
                 | beginning_statement
                 | for_statement
                 | case_statement
                 | repeat_statement
                 | while_statement '''
    if isinstance(p[1], (DefStatement, PutStatement, AddStatement,
                         ContinueUpStatement, ContinueDownStatement, ContinueRightStatement, ContinueLeftStatement,
                         PosStatement, PosXStatement, PosYStatement, UseColorStatement,
                         DownStatement, UpStatement, BeginningStatement)):
        p[0] = p[1]
    elif len(p) == 3 and p[2] == ';':
        p[0] = p[1]
    else:
        p[0] = Expression(p[1])

# Reglas para las expresiones aritméticas
def p_expression_binop(p):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression MULT_OP expression
                  | expression DIV_OP expression'''
    p[0] = BinaryOperation(p[1], p[2], p[3])

def p_expression_comparison(p):
    '''expression : expression LT expression
                  | expression GT expression
                  | expression EQUALS expression'''
    p[0] = BinaryOperation(p[1], p[2], p[3])

# Regla para definir variable
def p_def_statement(p):
    '''def_statement : DEF LPAREN ID COMMA expression RPAREN'''
    p[0] = DefStatement(p[3], p[5])  # Crea un nodo DefStatement con el nombre y el valor

# Regla para modificar variable
def p_put_statement(p):
    '''put_statement : PUT LPAREN ID COMMA expression RPAREN'''
    var_name = p[3]
    value = p[5]

    p[0] = PutStatement(var_name, value)  # Crea un nodo PutStatement

# Regla para la funcion ADD
def p_add_statement(p):
    '''add_statement : ADD LPAREN ID RPAREN
                     | ADD LPAREN ID COMMA expression RPAREN'''
    if len(p) == 5:
        p[0] = AddStatement(p[3])
    elif len(p) == 7:
        p[0] = AddStatement(p[3], p[5])

# Regla para el continueup
def p_continueup_statement(p):
    '''continueup_statement : CONTINUEUP expression '''
    p[0] = ContinueUpStatement(p[2])

# Regla para el continuedown
def p_continuedown_statement(p):
    '''continuedown_statement : CONTINUEDOWN expression'''
    p[0] = ContinueDownStatement(p[2])

# Regla para el continueright
def p_continueright_statement(p):
    '''continueright_statement : CONTINUERIGHT expression'''
    p[0] = ContinueRightStatement(p[2])

# Regla para el continueleft
def p_continueleft_statement(p):
    '''continueleft_statement : CONTINUELEFT expression'''
    p[0] = ContinueLeftStatement(p[2])

# Regla que modifica la posicion del lapiz
def p_pos_statement(p):
    '''pos_statement : POS LPAREN expression COMMA expression RPAREN'''
    p[0] = PosStatement(p[3], p[5])

def p_posx_statement(p):
    '''posx_statement : POSX expression'''
    p[0] = PosXStatement(p[2])

def p_posy_statement(p):
    '''posy_statement : POSY expression'''
    p[0] = PosYStatement(p[2])

def p_usecolor_statement(p):
    '''usecolor_statement : USECOLOR expression'''
    p[0] = UseColorStatement(p[2])

def p_down_statement(p):
    '''down_statement : DOWN'''
    p[0] = DownStatement()

def p_up_statement(p):
    '''up_statement : UP'''
    p[0] = UpStatement()

def p_beginning_statement(p):
    '''beginning_statement : BEGINNING'''
    p[0] = BeginningStatement()
# Regla que compara si dos expresiones son iguales
def p_equal_statement(p):
    '''expression : EQUAL LPAREN expression COMMA expression RPAREN'''
    p[0] = EqualStatement(p[3], p[5])

def p_and_statement(p):
    '''expression : AND LPAREN expression COMMA expression RPAREN'''
    p[0] = AndStatement(p[3], p[5])

def p_or_statement(p):
    '''expression : OR LPAREN expression COMMA expression RPAREN'''
    p[0] = OrStatement(p[3], p[5])

def p_greater_statement(p):
    '''expression : GREATER LPAREN expression COMMA expression RPAREN'''
    p[0] = GreaterStatement(p[3], p[5])

def p_smaller_statement(p):
    '''expression : SMALLER LPAREN expression COMMA expression RPAREN'''
    p[0] = SmallerStatement(p[3], p[5])

def p_substr_statement(p):
    '''expression : SUBSTR LPAREN expression COMMA expression RPAREN'''
    p[0] = SubstrStatement(p[3], p[5])

def p_random_statement(p):
    '''expression : RANDOM LPAREN expression RPAREN'''
    p[0] = RandomStatement(p[3])

def p_mult_statement(p):
    '''expression : MULT LPAREN expression COMMA expression RPAREN'''
    p[0] = MultStatement(p[3], p[5])

def p_div_statement(p):
    '''expression : DIV LPAREN expression COMMA expression RPAREN'''
    p[0] = DivStatement(p[3], p[5])

def p_sum_statement(p):
    '''expression : SUM LPAREN expression COMMA expression RPAREN'''
    p[0] = SumStatement(p[3], p[5])

def p_expression_group(p):
    'expression : LPAREN expression_list RPAREN'
    p[0] = ExpressionGroup(p[2])

def p_expression_bracket(p):
    '''expression_bracket : LBRACKET expression_list SEMI RBRACKET
                          | LBRACKET expression_list RBRACKET'''
    p[0] = ExpressionBracket(p[2])
# Regla para las expresiones booleanas
def p_expression_boolean(p):
    'expression : BOOLEAN'
    p[0] = BooleanExpression(p[1].lower() == 'true')  # Crea un nodo BooleanExpression con el valor booleano

# Regla para la pluralizacion de expresiones
def p_expression_list(p):
    '''expression_list : expression
                       | expression_list expression'''
    if len(p) == 2:
        p[0] = ExpressionList([p[1]])  # Caso base
    else:
        p[0] = ExpressionList(p[1].expressions + [p[2]])  # Concatenar listas de expresiones

# Regla para la manejar numeros
def p_expression_number(p):
    'expression : NUMBER'
    p[0] = NumberExpression(p[1])  # Crea un nodo NumberExpression con el valor del número
# Regla para manejar identificadores
def p_expression_id(p):
    'expression : ID'
    if p[1] in variables:
        p[0] = IdExpression(p[1])  # Crea un nodo IdExpression con el nombre de la variable
    else:
        p[0] = IdExpression(p[1])  # También podrías manejar el caso aquí si la variable no está definida
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

    # Crear un nodo ForStatement en lugar de ejecutar directamente
    p[0] = ForStatement(var_name, min_val, max_val, body)
# Regla para la ejecucion del for en un futuro
def p_execute_statement(p):
    '''execute_statement : statement'''
    p[0] = ExecuteStatement(p[1])  # Crea un nodo ExecuteStatement con el statement

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
    code = """
    Def(var,0)
    Def(result, Sum(var, 4))
    Put(var, result)
    var = 4 
    """
    # Analizar el código y obtener el AST
    ast_root = parse(code)
    print("AST:", ast_root)  # Para verificar que se construyó correctamente

    # Crear un visitor para ejecutar el AST
    visitor = ASTVisitor()  # Usa tu clase de visitor
    visitor.visit(ast_root)  # Ejecuta el árbol AST


