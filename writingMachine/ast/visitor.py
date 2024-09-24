import random

from writingMachine.ast.add_statement import AddStatement
from writingMachine.ast.and_statement import AndStatement
from writingMachine.ast.beginning_statement import BeginningStatement
from writingMachine.ast.binary_operation import BinaryOperation
from writingMachine.ast.boolean_expression import BooleanExpression
from writingMachine.ast.case_statement import CaseStatement
from writingMachine.ast.continuedown_statement import ContinueDownStatement
from writingMachine.ast.continueleft_statement import ContinueLeftStatement
from writingMachine.ast.continueright_statement import ContinueRightStatement
from writingMachine.ast.continueup_statement import ContinueUpStatement
from writingMachine.ast.def_statement import DefStatement
from writingMachine.ast.div_statement import DivStatement
from writingMachine.ast.down_statement import DownStatement
from writingMachine.ast.equal_statement import EqualStatement
from writingMachine.ast.execute_statement import ExecuteStatement
from writingMachine.ast.expression_bracket import ExpressionBracket
from writingMachine.ast.expression_group import ExpressionGroup
from writingMachine.ast.expression_list import ExpressionList
from writingMachine.ast.for_statement import ForStatement
from writingMachine.ast.greater_statement import GreaterStatement
from writingMachine.ast.id_expression import IdExpression
from writingMachine.ast.mult_statement import MultStatement
from writingMachine.ast.node import ASTNode
from writingMachine.ast.number_expression import NumberExpression
from writingMachine.ast.or_statement import OrStatement
from writingMachine.ast.pos_statement import PosStatement
from writingMachine.ast.posx_statement import PosXStatement
from writingMachine.ast.posy_statement import PosYStatement
from writingMachine.ast.put_statement import PutStatement
from writingMachine.ast.random_statement import RandomStatement
from writingMachine.ast.repeat_statement import RepeatStatement
from writingMachine.ast.smaller_statement import SmallerStatement
from writingMachine.ast.substr_statement import SubstrStatement
from writingMachine.ast.sum_statement import SumStatement
from writingMachine.ast.up_statement import UpStatement
from writingMachine.ast.usecolor_statement import UseColorStatement
from writingMachine.ast.variable_context import VariableContext
from writingMachine.ast.when_clause import WhenClause
from writingMachine.ast.while_statement import WhileStatement


class ASTVisitor:
    """Clase base para visitar los nodos del AST."""

    def __init__(self):
        self.variable_context = VariableContext()
        self.x_position = 0
        self.y_position = 0
        self.current_color = 1  # 1 para negro, 2 para rojo
        self.pen_down = False

    def visit(self, node):
        print(f"Visiting node: {type(node).__name__}")
        method_name = f'visit_{type(node).__name__.lower()}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        """Método genérico que será llamado si no existe un método específico para un nodo."""
        raise NotImplementedError(f'No se ha implementado visit_{type(node).__name__.lower()}')

    def visit_program(self, node):
        results = []
        for statement in node.statements:
            result = self.visit(statement)
            if result is not None:
                results.append(result)
        return results

    def visit_expression(self, node):
        print("Tipo de node.value:", type(node.value))
        if isinstance(node.value, (NumberExpression, BooleanExpression, IdExpression, BinaryOperation,
                                   SumStatement, AddStatement,AndStatement, BeginningStatement,
                                   ContinueDownStatement, ContinueUpStatement, ContinueRightStatement,
                                   ContinueLeftStatement, DefStatement, DivStatement, DownStatement, EqualStatement,
                                   ExecuteStatement, ExpressionBracket, ExpressionGroup,
                                   ExpressionList, GreaterStatement, MultStatement, OrStatement,
                                   PosStatement, PosXStatement, PosYStatement, PutStatement, RandomStatement,
                                   SmallerStatement, SubstrStatement, UpStatement, UseColorStatement,
                                   RepeatStatement, VariableContext, WhileStatement, ForStatement,
                                   CaseStatement, WhenClause)):
            return self.visit(node.value)
        return node.value

    def visit_defstatement(self, node):
        var_name = node.var_name
        value = self.visit(node.value)
        if var_name in self.variable_context.variables:
            print(f"Error: Variable '{var_name}' ya definida")
        else:
            self.variable_context.set_variable(var_name, value)
            print(f"Definido {node.var_name} = {value}")
        return value

    def visit_putstatement(self, node):
        var_name = node.var_name
        value = self.visit(node.value)
        if var_name in self.variable_context.variables:
            self.variable_context.set_variable(var_name, value)
            print(f"Actualizado {var_name} = {value}")
        else:
            print(f"Error: Variable '{var_name}' no definida")
        return value

    def visit_addstatement(self, node):
        if node.var_name not in self.variable_context.variables:
            print(f"Error: '{node.var_name}' no es una variable válida.")
            return None

        current_value = self.variable_context.get_variable(node.var_name)

        if node.increment_value is None:
            new_value = current_value + 1
        else:
            increment = self.visit(node.increment_value)
            if not isinstance(increment, (int, float)):
                print(f"Error: El incremento debe ser un número.")
                return None
            new_value = current_value + increment

        # Update the variable in the context
        self.variable_context.set_variable(node.var_name, new_value)
        print(f"Incrementado {node.var_name} de {current_value} a {new_value}")

        # Return the new value
        return new_value
    def visit_continueupstatement(self, node):
        move_units = self.visit(node.move_units)
        if isinstance(move_units, (int, float)):
            self.y_position += move_units
            result = f"Movido {move_units} unidades hacia arriba. Nueva posición en Y: {self.y_position}"
            print(result)
            return result
        else:
            print(f"Error: No se puede mover {move_units} unidades. Verifica el valor.")
            return None

    def visit_continuedownstatement(self, node):
        move_units = self.visit(node.move_units)
        if isinstance(move_units, (int, float)):
            self.y_position -= move_units
            result = f"Movido {move_units} unidades hacia abajo. Nueva posición en Y: {self.y_position}"
            print(result)
            return result
        else:
            print(f"Error: No se puede mover {move_units} unidades. Verifica el valor.")
            return None

    def visit_continuerightstatement(self, node):
        move_units = self.visit(node.move_units)
        if isinstance(move_units, (int, float)):
            self.x_position += move_units
            result = f"Movido {move_units} unidades hacia la derecha. Nueva posición en X: {self.x_position}"
            print(result)
            return result
        else:
            print(f"Error: No se puede mover {move_units} unidades. Verifica el valor.")
            return None

    def visit_continueleftstatement(self, node):
        move_units = self.visit(node.move_units)
        if isinstance(move_units, (int, float)):
            self.x_position -= move_units
            result = f"Movido {move_units} unidades hacia la izquierda. Nueva posición en X: {self.x_position}"
            print(result)
            return result
        else:
            print(f"Error: No se puede mover {move_units} unidades. Verifica el valor.")
            return None

    def visit_posstatement(self, node):
        x_val = self.visit(node.x_val)
        y_val = self.visit(node.y_val)
        self.x_position = x_val
        self.y_position = y_val
        result = f"Posición actualizada a X: {self.x_position}, Y: {self.y_position}"
        print(result)
        return result

    def visit_posxstatement(self, node):
        x_val = self.visit(node.x_val)
        self.x_position = x_val
        result = f"Posición actualizada a X: {self.x_position}, Y: {self.y_position}"
        print(result)
        return result

    def visit_posystatement(self, node):
        y_val = self.visit(node.y_val)
        self.y_position = y_val
        result = f"Posición actualizada a X: {self.x_position}, Y: {self.y_position}"
        print(result)
        return result

    def visit_usecolorstatement(self, node):
        color_value = self.visit(node.color_value)
        if color_value in [1, 2]:
            self.current_color = color_value
            color_name = "Negro" if color_value == 1 else "Rojo"
            result = f"Color cambiado a {color_name} (Compartimiento {self.current_color})"
        else:
            result = f"Error: {color_value} no es un color válido. Usa 1 (Negro) o 2 (Rojo)."
        print(result)
        return result

    def visit_downstatement(self, node):
        self.pen_down = True
        result = "Lapicero colocado en la superficie (Down)"
        print(result)
        return result

    def visit_upstatement(self, node):
        self.pen_down = False
        result = "Lapicero levantado de la superficie (Up)"
        print(result)
        return result

    def visit_beginningstatement(self, node):
        self.x_position = 1
        self.y_position = 1
        result = f"Lapicero colocado en la posición inicial: X: {self.x_position}, Y: {self.y_position}"
        print(result)
        return result

    def visit_equalstatement(self, node):
        left = node.left.accept(self)
        right = node.right.accept(self)
        result = left == right
        print(result)
        return result

    def visit_andstatement(self, node):
        left = node.left.accept(self)
        right = node.right.accept(self)
        result = bool(left) and bool(right)
        print(result)
        return result

    def visit_orstatement(self, node):
        left = node.left.accept(self)
        right = node.right.accept(self)
        result = bool(left) or bool(right)
        print(result)
        return result

    def visit_greaterstatement(self, node):
        left = node.left.accept(self)
        right = node.right.accept(self)
        result = left > right
        print(result)
        return result

    def visit_smallerstatement(self, node):
        left = node.left.accept(self)
        right = node.right.accept(self)
        result = left < right
        print(result)
        return result

    def visit_substrstatement(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        if left < right:
            raise ValueError("Error: N1 debe ser mayor o igual a N2.")
        result = left - right
        print(f"Sustracción: {left} - {right} = {result}")
        return result

    def visit_randomstatement(self, node):
        # Obtener el valor de n
        n = node.value.accept(self)  # Asegúrate de que node.value sea un nodo que pueda ser evaluado

        # Verificar que n sea un número válido
        if n < 0:
            raise ValueError("Error: n debe ser mayor o igual a 0.")

        # Generar un número aleatorio entre 0 y n
        result = random.randint(0, n)
        print(result)
        return result  # Retorna el número aleatorio generado

    def visit_multstatement(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        result = left * right
        print(f"Multiplicación: {left} * {right} = {result}")
        return result

    def visit_divstatement(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        if right == 0:
            raise ValueError("Error: División por cero no permitida.")
        result = left // right
        print(f"División: {left} // {right} = {result}")
        return result

    def visit_sumstatement(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        result = left + right
        print(f"Suma: {left} + {right} = {result}")
        return result

    def visit_forstatement(self, node):
        # Obtener los valores de min_value y max_value
        min_value = self.visit(node.min_value)
        max_value = self.visit(node.max_value)

        # Verificar si min_value es mayor o igual que max_value
        if min_value >= max_value:
            raise ValueError("Max debe ser mayor que Min en el bucle FOR.")

        # Crear la variable en el contexto
        if self.variable_context.get_variable(node.variable) is not None:
            raise ValueError(f"La variable '{node.variable}' ya existe.")

        # Inicializar la variable en el contexto
        self.variable_context.set_variable(node.variable, min_value)

        # Ejecutar el cuerpo del bucle
        for i in range(min_value, max_value):
            print(f"Iteración FOR: {i}")
            # Establecer el valor de la variable para la iteración actual
            self.variable_context.set_variable(node.variable, i)

            # Visitar cada declaración en el cuerpo del bucle
            for statement in node.body:
                print(f"  Ejecutando declaración: {statement}")
                self.visit(statement)
        # Eliminar la variable del contexto al finalizar el bucle
        self.variable_context.remove_variable(node.variable)

    def visit_casestatement(self, node):
        print(f"Ejecutando Case para la variable: {node.variable}")

        # Obtener el valor de la variable
        variable_value = self.variable_context.get_variable(node.variable)
        if variable_value is None:
            raise ValueError(f"La variable '{node.variable}' no está definida.")

        print(f"Valor de la variable: {variable_value}")

        # Evaluar cada cláusula When
        for when_clause in node.when_clauses:
            condition_value = self.visit(when_clause.condition)
            print(f"Evaluando condición: {condition_value}")

            if condition_value == variable_value:
                print("Condición cumplida, ejecutando cuerpo del When")
                for statement in when_clause.body:
                    print(f" Ejecutando declaración: {statement}")
                    self.visit(statement)
                return

        # Si ninguna condición se cumple y hay una cláusula Else, ejecutarla
        if node.else_clause:
            print("Ninguna condición cumplida, ejecutando cláusula Else")
            for statement in node.else_clause:
                print(f" Ejecutando declaración: {statement}")
                self.visit(statement)
        else:
            print("Ninguna condición cumplida y no hay cláusula Else")

    def visit_repeatstatement(self, node):
        iteration = 0
        while True:
            iteration += 1
            print(f"Iteración Repeat {iteration}")

            # Ejecutar el cuerpo
            for statement in node.body:
                print(f"  Ejecutando declaración: {statement}")
                self.visit(statement)

            # Verificar la condición
            condition_result = self.visit(node.condition)

            # Asegurarse de que tomamos solo el primer valor si es una lista
            if isinstance(condition_result, list):
                condition_result = condition_result[0]

            print(f"  Resultado de la condición: {condition_result}")

            if condition_result:
                print("Saliendo del bucle Repeat")
                break  # Salir del bucle si la condición es verdadera

    def visit_whilestatement(self, node):
        iteration = 0
        while True:
            iteration += 1
            print(f"Iteración While {iteration}")

            # Evaluar la condición
            condition_result = self.visit(node.condition)
            print(f"  Resultado de la condición: {condition_result}")

            # Asegúrate de que tomas solo el primer valor si es una lista
            if isinstance(condition_result, list):
                condition_result = condition_result[0]

            if not condition_result:
                print("Saliendo del bucle While")
                break

            # Ejecutar el cuerpo
            for statement in node.body:
                print(f"  Ejecutando declaración: {statement}")
                self.visit(statement)

    def visit_binaryoperation(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)

        if isinstance(left, list):
            left = left[0]
        if isinstance(right, list):
            right = right[0]

        # Imprimir los valores antes de realizar la operación
        print(f"Operando izquierdo: {left}, Operando derecho: {right}, Operador: {node.operator}")

        if node.operator == '+':
            result = left + right
            print(result)
            return result
        elif node.operator == '-':
            result = left - right
            print(result)
            return result
        elif node.operator == '*':
            result = left * right
            print(result)
            return result
        elif node.operator == '/':
            if right == 0:
                raise ValueError("División por cero")
            result = left / right
            print(result)
            return result
        elif node.operator == '<':
            result = left < right
            print(result)
            return result
        elif node.operator == '>':
            result = left > right
            print(result)
            return result
        elif node.operator == '=':
            result = left == right
            print(result)
            return result


    def visit_expressiongroup(self, node):
        # Aquí asumimos que node.expressions es una instancia de ExpressionList
        results = node.expressions.accept(self)  # Llama al visit para la lista de expresiones
        return results

    def visit_expressionbracket(self, node):
        # Visitar todas las expresiones en el corchete
        results = [expr.accept(self) for expr in node.expressions]
        return results  # Retorna los resultados de todas las expresiones

    def visit_expressionlist(self, node):
        results = []
        for expr in node.expressions:
            if isinstance(expr, str):
                # Si es una cadena, probablemente sea el nombre de un método de visita
                method_name = f'visit_{expr.lower()}'
                if hasattr(self, method_name):
                    result = getattr(self, method_name)(expr)
                else:
                    print(f"Error: No se encontró el método {method_name}")
                    result = None
            else:
                # Si no es una cadena, visita el nodo normalmente
                result = self.visit(expr)
            results.append(result)
        return results

    def evaluate(self, node):
        if isinstance(node, IdExpression):
            return self.variable_context.get_variable(node.var_name)
        elif isinstance(node, NumberExpression):
            return node.value
        else:
            return self.visit(node)

    def visit_idexpression(self, node):
        return self.variable_context.get_variable(node.var_name)
    def visit_numberexpression(self, node):
        return node.value

    def visit_booleanexpression(self, node):
        return node.value

    def print_ast(self, node, level=0):
        indent = "  " * level  # Indentar de acuerdo al nivel de profundidad
        print(f"{indent}{type(node).__name__}")  # Imprimir el tipo del nodo

        # Verificar los atributos de cada nodo
        for attr, value in vars(node).items():
            if isinstance(value, ASTNode):  # Si es un nodo AST, imprimir recursivamente
                print(f"{indent}  {attr}:")
                self.print_ast(value, level + 1)
            elif isinstance(value, (list, tuple)):  # Si es una lista o tupla de nodos
                print(f"{indent}  {attr}: [")
                for item in value:
                    if isinstance(item, ASTNode):
                        self.print_ast(item, level + 1)
                print(f"{indent}  ]")
            else:
                print(f"{indent}  {attr}: {value}")  # Si es un valor básico, lo imprime directamente
