import random

import ply.yacc as yacc
from analizadorLexico import tokens, reset_lexer  # Asegúrate de importar reset_lexer del lexer
from ast_custom.call_statement import CallStatement
from ast_custom.case_statement import CaseStatement
from ast_custom.expression_list import ExpressionList
from ast_custom.procedure_statement import ProcedureStatement
from ast_custom.repeat_statement import RepeatStatement
from ast_custom.substr_statement import SubstrStatement
from ast_custom.add_statement import AddStatement
from ast_custom.and_statement import AndStatement
from ast_custom.beginning_statement import BeginningStatement
from ast_custom.binary_operation import BinaryOperation
from ast_custom.boolean_expression import BooleanExpression
from ast_custom.continuedown_statement import ContinueDownStatement
from ast_custom.continueleft_statement import ContinueLeftStatement
from ast_custom.continueright_statement import ContinueRightStatement
from ast_custom.continueup_statement import ContinueUpStatement
from ast_custom.def_statement import DefStatement
from ast_custom.div_statement import DivStatement
from ast_custom.down_statement import DownStatement
from ast_custom.equal_statement import EqualStatement
from ast_custom.execute_statement import ExecuteStatement
from ast_custom.expression import Expression
from ast_custom.expression_bracket import ExpressionBracket
from ast_custom.expression_group import ExpressionGroup
from ast_custom.for_statement import ForStatement
from ast_custom.greater_statement import GreaterStatement
from ast_custom.id_expression import IdExpression
from ast_custom.mult_statement import MultStatement
from ast_custom.number_expression import NumberExpression
from ast_custom.or_statement import OrStatement
from ast_custom.pos_statement import PosStatement
from ast_custom.posx_statement import PosXStatement
from ast_custom.posy_statement import PosYStatement
from ast_custom.program import Program
from ast_custom.put_statement import PutStatement
from ast_custom.random_statement import RandomStatement
from ast_custom.smaller_statement import SmallerStatement
from ast_custom.sum_statement import SumStatement
from ast_custom.up_statement import UpStatement
from ast_custom.usecolor_statement import UseColorStatement
from ast_custom.visitor import ASTVisitor
from ast_custom.when_clause import WhenClause
from ast_custom.while_statement import WhileStatement

# Jerarquia de palabras
precedence = (
    ('left', 'OR'),        # Operador OR
    ('left', 'AND'),       # Operador AND
    ('left', 'EQUAL', 'SMALLER', 'GREATER', 'EQUALS',
     'LT', 'GT'),  # Comparaciones
    ('left', 'PLUS', 'MINUS', 'SUM', 'SUBSTR'),   # Suma y resta
    ('left', 'MULT_OP', 'DIV_OP', 'MULT', 'DIV'),  # Multiplicacion y division
)
# Variables necesarias
variables = {}
x_position = 1  # Posicion inicial en el eje x
y_position = 1  # Posicion inicial en el eje y
current_color = 1  # 1: Negro, 2: Rojo
syntax_errors = []

# Regla inicial (punto de entrada)
def p_program(p):
    '''program : statement SEMI
               | statement
               | program statement SEMI
               | program statement'''
    if len(p) == 2:  # Solo un statement
        p[0] = Program([p[1]])  # Crea un nodo Program con una lista que contiene un statement
    elif len(p) == 3:  # Un statement sin SEMI
        p[0] = Program([p[1]])  # Crea un nodo Program con una lista que contiene un statement
    else:  # Viene de program statement SEMI o program statement
        if hasattr(p[1], 'statements'):
            # Asegurate de que p[1] tenga el atributo statements
            p[0] = Program(p[1].statements + [p[2]])
        else:
            # Si p[1] no tiene el atributo statements, es un solo statement
            p[0] = Program([p[1]] + [p[2]])  # Asegurate de que se maneje correctamente
# produccion statment para casos de control
def p_statement(p):
    '''statement : expression
                 | procedure_statement
                 | call_statement
                 | def_statement
                 | put_statement
                 | add_statement
                 | continueup_statement
                 | continuedown_statement
                 | continueright_statement
                 | continueleft_statement
                 | turnright_statement
                 | turnleft_statement
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
                 | while_statement'''
    if isinstance(p[1], (DefStatement, PutStatement, AddStatement,
                         ContinueUpStatement, ContinueDownStatement, ContinueRightStatement, ContinueLeftStatement,
                         PosStatement, PosXStatement, PosYStatement, UseColorStatement,
                         DownStatement, UpStatement, BeginningStatement, ProcedureStatement, CallStatement)):
        p[0] = p[1]
    elif len(p) == 3 and p[2] == ';':
        p[0] = p[1]
    else:
        p[0] = Expression(p[1])

# Reglas para las expresiones aritmeticas
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
    '''def_statement : DEF LPAREN ID COMMA statement RPAREN'''
    p[0] = DefStatement(p[3], p[5])  # Crea un nodo DefStatement con el nombre y el valor

# Regla para modificar variable
def p_put_statement(p):
    '''put_statement : PUT LPAREN ID COMMA statement RPAREN'''
    var_name = p[3]
    value = p[5]

    p[0] = PutStatement(var_name, value)  # Crea un nodo PutStatement

# Regla para la funcion ADD
def p_add_statement(p):
    '''add_statement : ADD LPAREN ID RPAREN
                     | ADD LPAREN ID COMMA statement RPAREN'''
    if len(p) == 5:
        p[0] = AddStatement(p[3])
    elif len(p) == 7:
        p[0] = AddStatement(p[3], p[5])

# Regla para el continueup
def p_continueup_statement(p):
    '''continueup_statement : CONTINUEUP statement '''
    p[0] = ContinueUpStatement(p[2])

# Regla para el continuedown
def p_continuedown_statement(p):
    '''continuedown_statement : CONTINUEDOWN statement'''
    p[0] = ContinueDownStatement(p[2])

# Regla para el continueright
def p_continueright_statement(p):
    '''continueright_statement : CONTINUERIGHT statement'''
    p[0] = ContinueRightStatement(p[2])

# Regla para el continueleft
def p_continueleft_statement(p):
    '''continueleft_statement : CONTINUELEFT statement'''
    p[0] = ContinueLeftStatement(p[2])

# Regla para el TurnRight
def p_turnright_statement(p):
    '''turnright_statement : TURNRIGHT statement'''
    p[0] = ContinueLeftStatement(p[2])

# Regla para el TurnLeft
def p_turnleft_statement(p):
    '''turnleft_statement : TURNLEFT statement'''
    p[0] = ContinueLeftStatement(p[2])

# Regla que modifica la posicion del lapiz
def p_pos_statement(p):
    '''pos_statement : POS LPAREN statement COMMA statement RPAREN'''
    p[0] = PosStatement(p[3], p[5])

def p_posx_statement(p):
    '''posx_statement : POSX statement'''
    p[0] = PosXStatement(p[2])

def p_posy_statement(p):
    '''posy_statement : POSY statement'''
    p[0] = PosYStatement(p[2])

def p_usecolor_statement(p):
    '''usecolor_statement : USECOLOR statement'''
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
    '''expression : EQUAL LPAREN statement COMMA statement RPAREN'''
    p[0] = EqualStatement(p[3], p[5])

def p_and_statement(p):
    '''expression : AND LPAREN statement COMMA statement RPAREN'''
    p[0] = AndStatement(p[3], p[5])

def p_or_statement(p):
    '''expression : OR LPAREN statement COMMA statement RPAREN'''
    p[0] = OrStatement(p[3], p[5])

def p_greater_statement(p):
    '''expression : GREATER LPAREN statement COMMA statement RPAREN'''
    p[0] = GreaterStatement(p[3], p[5])

def p_smaller_statement(p):
    '''expression : SMALLER LPAREN statement COMMA statement RPAREN'''
    p[0] = SmallerStatement(p[3], p[5])

def p_substr_statement(p):
    '''expression : SUBSTR LPAREN statement COMMA statement RPAREN'''
    p[0] = SubstrStatement(p[3], p[5])

def p_random_statement(p):
    '''expression : RANDOM LPAREN statement RPAREN'''
    p[0] = RandomStatement(p[3])

def p_mult_statement(p):
    '''expression : MULT LPAREN statement COMMA statement RPAREN'''
    p[0] = MultStatement(p[3], p[5])

def p_div_statement(p):
    '''expression : DIV LPAREN statement COMMA statement RPAREN'''
    p[0] = DivStatement(p[3], p[5])

def p_sum_statement(p):
    '''expression : SUM LPAREN statement COMMA statement RPAREN'''
    p[0] = SumStatement(p[3], p[5])

def p_expression_group(p):
    'expression : LPAREN expression_list RPAREN'
    p[0] = ExpressionGroup(p[2])

def p_expression_bracket(p):
    '''expression_bracket : LBRACKET expression_list RBRACKET
                          | LBRACKET expression_list SEMI RBRACKET'''
    p[0] = ExpressionBracket(p[2])
# Regla para las expresiones booleanas
def p_expression_boolean(p):
    'expression : BOOLEAN'
    p[0] = BooleanExpression(p[1].lower() == 'true')  # Crea un nodo BooleanExpression con el valor booleano

# Regla para la pluralizacion de expresiones
def p_expression_list(p):
    '''expression_list : statement
                       | expression_list statement'''
    if len(p) == 2:
        p[0] = ExpressionList([p[1]])  # Caso base
    else:
        p[0] = ExpressionList(p[1].expressions + [p[2]])  # Concatenar listas de expresiones

# Regla para la manejar numeros
def p_expression_number(p):
    'expression : NUMBER'
    p[0] = NumberExpression(p[1])  # Crea un nodo NumberExpression con el valor del numero
# Regla para manejar identificadores
def p_expression_id(p):
    'expression : ID'
    if p[1] in variables:
        p[0] = IdExpression(p[1])  # Crea un nodo IdExpression con el nombre de la variable
    else:
        p[0] = IdExpression(p[1])  # Tambien podrias manejar el caso aqui si la variable no esta definida
# Regla para la definicion del control for
def p_for_statement(p):
    '''for_statement : FOR ID LPAREN expression TO expression RPAREN LOOP LBRACKET program RBRACKET END LOOP'''

    p[0] = ForStatement(variable=p[2], min_value=p[4], max_value=p[6], body=p[10])

# Regla para la ejecucion del for en un futuro
def p_execute_statement(p):
    '''execute_statement : statement'''
    p[0] = ExecuteStatement(p[1])  # Crea un nodo ExecuteStatement con el statement

# Regla para el control case
def p_case_statement(p):
    '''case_statement : CASE ID when_clauses END CASE
                      | CASE ID when_clauses ELSE LBRACKET program RBRACKET END CASE'''
    if len(p) == 6:
        p[0] = CaseStatement(variable=p[2], when_clauses=p[3], else_clause=None)
    else:
        p[0] = CaseStatement(variable=p[2], when_clauses=p[3], else_clause=p[6])

def p_when_clauses(p):
    '''when_clauses : when_clause
                    | when_clauses when_clause'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_when_clause(p):
    '''when_clause : WHEN expression THEN LBRACKET program RBRACKET'''
    p[0] = WhenClause(condition=p[2], body=p[5])
# Regla para el control repeat
def p_repeat_statement(p):
    '''repeat_statement : REPEAT LBRACKET program RBRACKET UNTIL LBRACKET statement RBRACKET'''
    p[0] = RepeatStatement(body=p[3], condition=p[7])
# Regla para el control While
def p_while_statement(p):
    '''while_statement : WHILE LBRACKET statement RBRACKET LBRACKET program RBRACKET WHEND'''
    p[0] = WhileStatement(condition=p[3], body=p[6])  # La condicion se toma de p[3] y el cuerpo de p[6]

def p_procedure_statement(p):
    '''procedure_statement : PROC ID LPAREN parameter_list RPAREN LBRACKET program RBRACKET SEMI END'''
    p[0] = ProcedureStatement(procedure_name=p[2], arguments=p[4], body=p[7])

def p_call_statement(p):
    '''call_statement : CALL ID LPAREN parameter_list RPAREN'''
    p[0] = CallStatement(procedure_name=p[2], arguments=p[4])

def p_parameter_list(p):
    '''parameter_list : expression
                      | parameter_list COMMA expression
                      | '''  # Deja esta línea vacía para indicar que puede ser una lista vacía
    if len(p) == 2:
        p[0] = [p[1]]  # Una sola expresión
    elif len(p) == 4:
        p[0] = p[1] + [p[3]]  # Agrega la expresión a la lista existente
    else:
        p[0] = []  # No hay parámetros, lista vacía

# Regla para manejo de errores
def p_error(p):
    global syntax_errors
    if p:
        print(f"Error de sintaxis: simbolo inesperado '{p.value}' en la linea {p.lineno}")
        syntax_errors.append(f"Error de sintaxis: simbolo inesperado '{p.value}' en la linea {p.lineno}")
    else:
        print(f"Error de sintaxis: Se esperaba mas input pero no se encontro.")
        syntax_errors.append("Error de sintaxis: Se esperaba mas input pero no se encontro.")

# Construir el parser
parser = yacc.yacc()


def reset_parser():
    global variables, x_position, y_position, current_color, syntax_errors
    variables = {}
    x_position = 1
    y_position = 1
    current_color = 1
    syntax_errors = []
    reset_lexer()  # Reinicia también el lexer


# Modificar la función de análisis sintáctico
def parse(input_string):
    reset_parser()  # Reinicia el estado del parser y lexer

    # Separar el input en líneas
    lines = input_string.strip().splitlines()

    # Filtrar las líneas que no comienzan con '//'
    filtered_lines = [line for line in lines if not line.strip().startswith('//')]

    # Unir las líneas restantes
    processed_code = "\n".join(filtered_lines)

    # Ahora, parsear el código procesado
    return parser.parse(processed_code, tracking=True)


# Ejemplo de prueba
if __name__ == "__main__":
    code = """
    //hola
    Proc Ayu ()
    [
    Def(car, 2);
    Def(car,1);
    Or(true,true);
    ];
    end;
    
    
    Proc Main ()
    [
    Def(car,5);
    call Ayu ();
    ];
    end;
    //buenas
    """
    # Analizar el codigo y obtener el AST
    ast_root = parse(code)
    print("AST:", ast_root)  # Para verificar que se construyo correctamente

    # Crear un visitor para ejecutar el AST
    visitor = ASTVisitor()  # Usa tu clase de visitor
    visitor.visit(ast_root)  # Ejecuta el arbol AST

    #visitor.print_ast(ast_root)
    visitor.print_symbol_table()

    #visitor.print_procedure_tracker()



