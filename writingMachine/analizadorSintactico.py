import random

import ply.yacc as yacc
from analizadorLexico import tokens
from writingMachine.ast.case_statement import CaseStatement
from writingMachine.ast.expression_list import ExpressionList
from writingMachine.ast.repeat_statement import RepeatStatement
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
from writingMachine.ast.when_clause import WhenClause
from writingMachine.ast.while_statement import WhileStatement

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
    if len(p) == 2:  # Solo un statement
        p[0] = Program([p[1]])  # Crea un nodo Program con una lista que contiene un statement
    elif len(p) == 3:  # Un statement sin SEMI
        p[0] = Program([p[1]])  # Crea un nodo Program con una lista que contiene un statement
    else:  # Viene de program statement SEMI o program statement
        if hasattr(p[1], 'statements'):
            # Asegúrate de que p[1] tenga el atributo statements
            p[0] = Program(p[1].statements + [p[2]])
        else:
            # Si p[1] no tiene el atributo statements, es un solo statement
            p[0] = Program([p[1]] + [p[2]])  # Asegúrate de que se maneje correctamente
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
                 | while_statement'''
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
    '''repeat_statement : REPEAT LBRACKET program RBRACKET UNTIL LBRACKET program RBRACKET'''
    p[0] = RepeatStatement(body=p[3], condition=p[7])
# Regla para el control While
def p_while_statement(p):
    '''while_statement : WHILE LBRACKET program RBRACKET LBRACKET program RBRACKET WHEND'''
    p[0] = WhileStatement(condition=p[3], body=p[6])  # La condición se toma de p[3] y el cuerpo de p[6]

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
    Def(var4,True);
    Put(var4, 5>6);
    Def(var,1);
    Def(var2, 8*8); 
    Put(var, var2); 
    Add(var); 
    Add(var, Div(5,var2)); 
    ContinueUp 5*(4-3); 
    ContinueDown var2; 
    ContinueRight Mult(var,2); 
    ContinueLeft 2; 
    Pos(var, Substr(var, 1)); 
    PosX 5*5; 
    PosY var2*5; 
    UseColor 2; 
    Down; 
    Up; 
    Beginning; 
    Equal(var1, var2); 
    Def(var3,True); 
    Equal(true,var3); 
    And(var3,true); 
    Or(var3,false); 
    Greater(3, 5*4); 
    Smaller(3, 5/1); 
    Random(var2); 
    Put(var, Sum(var,4)); Put(var, Substr(var,var)); 
    Repeat 
        [Add(var); Up;] 
    Until [var = 2];
    
    While [Smaller(var, 4)] 
        [ContinueLeft 1*2; Add(var);] 
    Whend; 
    For i(2 to 4) Loop 
        [Add(var,3+8)] 
    End Loop; 
    
    Put(var, 3); 
    
    Case var 
        When 1 Then 
            [Up] 
        When 2 Then 
            [Down] 
        When 3 Then 
            [Add(var)]
    End Case; 
    For x(0 to 3) Loop 
        [Case x 
            When 0 Then 
                [Up] 
            When 1 Then 
                [Down] 
            Else 
                [Add(var)] 
        End Case] 
    End Loop; 
    """
    # Analizar el código y obtener el AST
    ast_root = parse(code)
    print("AST:", ast_root)  # Para verificar que se construyó correctamente

    # Crear un visitor para ejecutar el AST
    visitor = ASTVisitor()  # Usa tu clase de visitor
    visitor.visit(ast_root)  # Ejecuta el árbol AST

    visitor.print_ast(ast_root)
    visitor.print_symbol_table()



