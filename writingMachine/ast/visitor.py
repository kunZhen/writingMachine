import random
import re
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
from writingMachine.ast.procedure_statement import ProcedureStatement
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
        self.semantic_errors = []

    def visit(self, node):
        if node is None:
            # Manejo de nodo None
            self.semantic_errors.append("Error Semantico: Se encontro un nodo 'None' en el AST.")
            return


        method_name = f'visit_{type(node).__name__.lower()}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        """Metodo generico que sera llamado si no existe un metodo especifico para un nodo."""
        raise NotImplementedError(f'No se ha implementado visit_{type(node).__name__.lower()}')

    def visit_program(self, node):
        results = []
        for statement in node.statements:
            result = self.visit(statement)
            if result is not None:
                results.append(result)
        return results

    def visit_expression(self, node):
        if isinstance(node.value, (NumberExpression, BooleanExpression, IdExpression, BinaryOperation,
                                   SumStatement, AddStatement,AndStatement, BeginningStatement,
                                   ContinueDownStatement, ContinueUpStatement, ContinueRightStatement,
                                   ContinueLeftStatement, DefStatement, DivStatement, DownStatement, EqualStatement,
                                   ExecuteStatement, ExpressionBracket, ExpressionGroup,
                                   ExpressionList, GreaterStatement, MultStatement, OrStatement,
                                   PosStatement, PosXStatement, PosYStatement, PutStatement, RandomStatement,
                                   SmallerStatement, SubstrStatement, UpStatement, UseColorStatement,
                                   RepeatStatement, VariableContext, WhileStatement, ForStatement,
                                   CaseStatement, WhenClause, ProcedureStatement)):
            return self.visit(node.value)
        return node.value

    def visit_defstatement(self, node):
        var_name = node.var_name
        value = self.visit(node.value)  # Llama a visit para obtener el valor

        # Reglas para el nombre de la variable: min 3, max 10, empieza con minúscula,
        # contiene letras, números, _ y @.
        if not re.match(r'^[a-z][a-zA-Z0-9_@]{2,9}$', var_name):
            error_msg = (f"Error Semántico: El nombre de la variable '{var_name}' no cumple "
                         "con las reglas. Debe tener entre 3 y 10 caracteres, comenzar con "
                         "una letra minúscula, y puede contener letras, números, '_' y '@'.")
            print(error_msg)
            self.semantic_errors.append(error_msg)
            return None

        # Determinar el tipo basado en el valor del nodo
        if str(value) == 'True' or str(value) == 'False':
            var_type = "BOOLEAN"
        elif isinstance(value, int):
            var_type = "NUMBER"
        elif isinstance(node.value, IdExpression):
            var_type = "ID"
        else:
            var_type = "UNKNOWN"

        # Verificar si la variable ya está definida y si el tipo coincide
        if var_name in self.variable_context.variables:
            existing_type = self.variable_context.get_variable_type(var_name)
            if existing_type != var_type:
                error_msg = (f"Error Semántico: La variable '{var_name}' ya está definida como '{existing_type}', "
                             f"pero se intenta redefinir como '{var_type}'.")
                print(error_msg)
                self.semantic_errors.append(error_msg)
                return None  # O lanza una excepción, según tu diseño

        # Si la variable no está definida o los tipos coinciden, se define o redefine
        self.variable_context.set_variable(var_name, value, var_type)
        print(f"Definido {var_name} = {value} (Tipo: {var_type})")

        return value

    def visit_putstatement(self, node):
        var_name = node.var_name
        value = self.visit(node.value)

        if var_name in self.variable_context.variables:
            current_type = self.variable_context.get_variable_type(var_name)
            # Determinar el tipo del nuevo valor
            if str(value) == 'True':
                new_type = "BOOLEAN"
            elif str(value) == 'False':
                new_type = "BOOLEAN"
            elif isinstance(value, int):
                new_type = "NUMBER"
            elif isinstance(node.value, IdExpression):
                new_type = "ID"
            else:
                new_type = "UNKNOWN"

            # Comprobar si los tipos coinciden
            if new_type != current_type:
                print(f"Error Semantico: No se puede asignar '{value}' de tipo '{new_type}' a "
                      f"la variable '{var_name}' que es de tipo '{current_type}'.")
                return None  # O lanza una excepcion segun tu diseño

            # Si los tipos coinciden, actualiza la variable
            self.variable_context.set_variable(var_name, value, current_type)
            print(f"Actualizado {var_name} = {value}")
        else:
            print(f"Error Semantico: La variable '{var_name}' no esta definida.")
            self.semantic_errors.append(
                f"Error Semantico: La variable '{var_name}' no esta definida.")

    def visit_addstatement(self, node):
        if node.var_name not in self.variable_context.variables:
            print(f"Error Semantico: '{node.var_name}' no es una variable valida.")
            self.semantic_errors.append(
                f"Error Semantico: '{node.var_name}' no es una variable valida.")
            return None

        current_value = self.variable_context.get_variable(node.var_name)
        current_type = self.variable_context.get_variable_type(node.var_name)

        # Comprobar si la variable es de tipo numerico
        if current_type != "NUMBER":
            print(f"Error Semantico: No se puede incrementar '{node.var_name}' de tipo '{current_type}'.")
            self.semantic_errors.append(f"Error Semantico: No se puede incrementar '{node.var_name}' de tipo '{current_type}'.")
            return None

        if node.increment_value is None:
            new_value = current_value + 1
        else:
            increment = self.visit(node.increment_value)

            # Verificar que el incremento sea un numero
            if str(increment) == 'True':
                print(
                    f"Error Semantico: El incremento debe ser un numero, pero se obtuvo '{increment}' de tipo '{type(increment).__name__}'.")
                self.semantic_errors.append(f"Error Semantico: El incremento debe ser un numero, pero se obtuvo '{increment}' de tipo '{type(increment).__name__}'.")

                return None
            elif str(increment) == 'False':
                print(
                    f"Error Semantico: El incremento debe ser un numero, pero se obtuvo '{increment}' de tipo '{type(increment).__name__}'.")
                self.semantic_errors.append(
                    f"Error Semantico: El incremento debe ser un numero, pero se obtuvo '{increment}' de tipo '{type(increment).__name__}'.")
                return None

            new_value = current_value + increment

        # Actualizar la variable en el contexto
        self.variable_context.set_variable(node.var_name, new_value, current_type)
        print(f"Incrementado {node.var_name} de {current_value} a {new_value}")

        # Retornar el nuevo valor
        return new_value

    def visit_continueupstatement(self, node):
        move_units = self.visit(node.move_units)
        if str(move_units) == 'True' or str(move_units) == 'False':
            print(f"Error Semantico: No se puede mover '{move_units}' unidades. Se esperaba un numero.")
            self.semantic_errors.append(f"Error Semantico: No se puede mover '{move_units}' unidades. Se esperaba un numero.")
            return None
        elif isinstance(move_units, (int, float)):
            self.y_position += move_units
            result = f"Movido {move_units} unidades hacia arriba. Nueva posicion en Y: {self.y_position}"
            print(result)
            return result
        else:
            print(f"Error Semantico: No se puede mover '{move_units}' unidades. Se esperaba un numero.")
            return None

    def visit_continuedownstatement(self, node):
        move_units = self.visit(node.move_units)
        if str(move_units) == 'True' or str(move_units) == 'False':
            print(f"Error Semantico: No se puede mover '{move_units}' unidades. Se esperaba un numero.")
            self.semantic_errors.append(f"Error Semantico: No se puede mover '{move_units}' unidades. Se esperaba un numero.")
            return None
        elif isinstance(move_units, (int, float)):
            self.y_position -= move_units
            result = f"Movido {move_units} unidades hacia abajo. Nueva posicion en Y: {self.y_position}"
            print(result)
            return result
        else:
            print(f"Error Semantico: No se puede mover '{move_units}' unidades. Se esperaba un numero.")
            return None

    def visit_continuerightstatement(self, node):
        move_units = self.visit(node.move_units)
        if str(move_units) == 'True' or str(move_units) == 'False':
            print(f"Error Semantico: No se puede mover '{move_units}' unidades. Se esperaba un numero.")
            self.semantic_errors.append(f"Error Semantico: No se puede mover '{move_units}' unidades. Se esperaba un numero.")
            return None
        elif isinstance(move_units, (int, float)):
            self.x_position += move_units
            result = f"Movido {move_units} unidades hacia la derecha. Nueva posicion en X: {self.x_position}"
            print(result)
            return result
        else:
            print(f"Error Semantico: No se puede mover '{move_units}' unidades. Se esperaba un numero.")
            return None

    def visit_continueleftstatement(self, node):
        move_units = self.visit(node.move_units)
        if str(move_units) == 'True' or str(move_units) == 'False':
            print(f"Error Semantico: No se puede mover '{move_units}' unidades. Se esperaba un numero.")
            self.semantic_errors.append(f"Error Semantico: No se puede mover '{move_units}' unidades. Se esperaba un numero.")
            return None
        elif isinstance(move_units, (int, float)):
            self.x_position -= move_units
            result = f"Movido {move_units} unidades hacia la izquierda. Nueva posicion en X: {self.x_position}"
            print(result)
            return result
        else:
            print(f"Error Semantico: No se puede mover '{move_units}' unidades. Se esperaba un numero.")
            return None

    def visit_posstatement(self, node):
        x_val = self.visit(node.x_val)
        y_val = self.visit(node.y_val)

        if str(x_val) == 'True' or str(x_val) == 'False':
            print(
                f"Error Semantico: La posicion X no puede ser un booleano. Se obtuvo '{x_val}' de tipo '{type(x_val).__name__}'.")
            self.semantic_errors.append(f"Error Semantico: La posicion X no puede ser un booleano. Se obtuvo '{x_val}' de tipo '{type(x_val).__name__}'.")
            return None

        if str(y_val) == 'True' or str(y_val) == 'False':
            print(
                f"Error Semantico: La posicion Y no puede ser un booleano. Se obtuvo '{y_val}' de tipo '{type(y_val).__name__}'.")
            self.semantic_errors.append(f"Error Semantico: La posicion Y no puede ser un booleano. Se obtuvo '{y_val}' de tipo '{type(y_val).__name__}'.")
            return None

        self.x_position = x_val
        self.y_position = y_val
        result = f"Posicion actualizada a X: {self.x_position}, Y: {self.y_position}"
        print(result)
        return result

    def visit_posxstatement(self, node):
        x_val = self.visit(node.x_val)

        if str(x_val) == 'True' or str(x_val) == 'False':
            print(
                f"Error Semantico: La posicion X no puede ser un booleano. Se obtuvo '{x_val}' de tipo '{type(x_val).__name__}'.")
            self.semantic_errors.append(f"Error Semantico: La posicion X no puede ser un booleano. Se obtuvo '{x_val}' de tipo '{type(x_val).__name__}'.")
            return None

        self.x_position = x_val
        result = f"Posicion actualizada a X: {self.x_position}, Y: {self.y_position}"
        print(result)
        return result

    def visit_posystatement(self, node):
        y_val = self.visit(node.y_val)

        if str(y_val) == 'True' or str(y_val) == 'False':
            print(
                f"Error Semantico: La posicion Y no puede ser un booleano. Se obtuvo '{y_val}' de tipo '{type(y_val).__name__}'.")
            self.semantic_errors.append(f"Error Semantico: La posicion Y no puede ser un booleano. Se obtuvo '{y_val}' de tipo '{type(y_val).__name__}'.")
            return None

        self.y_position = y_val
        result = f"Posicion actualizada a X: {self.x_position}, Y: {self.y_position}"
        print(result)
        return result

    def visit_usecolorstatement(self, node):
        color_value = self.visit(node.color_value)
        if color_value in [1, 2]:
            self.current_color = color_value
            color_name = "Negro" if color_value == 1 else "Rojo"
            result = f"Color cambiado a {color_name} (Compartimiento {self.current_color})"
        else:
            result = f"Error: {color_value} no es un color valido. Usa 1 (Negro) o 2 (Rojo)."
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
        result = f"Lapicero colocado en la posicion inicial: X: {self.x_position}, Y: {self.y_position}"
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

        # Verificar que left y right no sean booleanos
        if str(left) == 'True' or str(left) == 'False':
            print(
                f"Error Semantico: El valor izquierdo no puede ser un booleano. Se obtuvo '{left}' de tipo '{type(left).__name__}'.")
            self.semantic_errors.append(f"Error Semantico: El valor izquierdo no puede ser un booleano. Se obtuvo '{left}' de tipo '{type(left).__name__}'.")
            return None

        if str(right) == 'True' or str(right) == 'False':
            print(
                f"Error Semantico: El valor derecho no puede ser un booleano. Se obtuvo '{right}' de tipo '{type(right).__name__}'.")
            self.semantic_errors.append(
                f"Error Semantico: El valor derecho no puede ser un booleano. Se obtuvo '{right}' de tipo '{type(right).__name__}'.")
            return None

        result = left > right
        print(result)
        return result

    def visit_smallerstatement(self, node):
        left = node.left.accept(self)
        right = node.right.accept(self)

        # Verificar que left y right no sean booleanos
        if str(left) == 'True' or str(left) == 'False':
            print(
                f"Error Semantico: El valor izquierdo no puede ser un booleano. Se obtuvo '{left}' de tipo '{type(left).__name__}'.")
            self.semantic_errors.append(
                f"Error Semantico: El valor izquierdo no puede ser un booleano. Se obtuvo '{left}' de tipo '{type(left).__name__}'.")
            return None

        if str(right) == 'True' or str(right) == 'False':
            print(
                f"Error Semantico: El valor derecho no puede ser un booleano. Se obtuvo '{right}' de tipo '{type(right).__name__}'.")
            self.semantic_errors.append(
                f"Error Semantico: El valor derecho no puede ser un booleano. Se obtuvo '{right}' de tipo '{type(right).__name__}'.")
            return None

        result = left < right
        print(result)
        return result

    def visit_substrstatement(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)

        # Verificar que left y right no sean booleanos
        if str(left) == 'True' or str(left) == 'False':
            print(
                f"Error Semantico: El valor izquierdo no puede ser un booleano. Se obtuvo '{left}' de tipo '{type(left).__name__}'.")
            self.semantic_errors.append(
                f"Error Semantico: El valor izquierdo no puede ser un booleano. Se obtuvo '{left}' de tipo '{type(left).__name__}'.")
            return None

        if str(right) == 'True' or str(right) == 'False':
            print(
                f"Error Semantico: El valor derecho no puede ser un booleano. Se obtuvo '{right}' de tipo '{type(right).__name__}'.")
            self.semantic_errors.append(
                f"Error Semantico: El valor derecho no puede ser un booleano. Se obtuvo '{right}' de tipo '{type(right).__name__}'.")
            return None

        if left < right:
            raise ValueError("Error: N1 debe ser mayor o igual a N2.")

        result = left - right
        print(f"Sustraccion: {left} - {right} = {result}")
        return result

    def visit_randomstatement(self, node):
        # Obtener el valor de n
        n = node.value.accept(self)  # Asegurate de que node.value sea un nodo que pueda ser evaluado

        # Verificar que n no sea un booleano
        if str(n) == 'True' or str(n) == 'False':
            print(f"Error Semantico: n no puede ser un booleano. Se obtuvo '{n}' de tipo '{type(n).__name__}'.")
            self.semantic_errors.append(f"Error Semantico: n no puede ser un booleano. Se obtuvo '{n}' de tipo '{type(n).__name__}'.")
            return None

        # Verificar que n sea un numero valido
        if n < 0:
            raise ValueError("Error: n debe ser mayor o igual a 0.")

        # Generar un numero aleatorio entre 0 y n
        result = random.randint(0, n)
        print(result)
        return result  # Retorna el numero aleatorio generado

    def visit_multstatement(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)

        # Verificar que left y right no sean booleanos
        if str(left) == 'True' or str(left) == 'False':
            print(
                f"Error Semantico: El valor izquierdo no puede ser un booleano. Se obtuvo '{left}' de tipo '{type(left).__name__}'.")
            self.semantic_errors.append(
                f"Error Semantico: El valor izquierdo no puede ser un booleano. Se obtuvo '{left}' de tipo '{type(left).__name__}'.")
            return None

        if str(right) == 'True' or str(right) == 'False':
            print(
                f"Error Semantico: El valor derecho no puede ser un booleano. Se obtuvo '{right}' de tipo '{type(right).__name__}'.")
            self.semantic_errors.append(
                f"Error Semantico: El valor derecho no puede ser un booleano. Se obtuvo '{right}' de tipo '{type(right).__name__}'.")
            return None

        result = left * right
        print(f"Multiplicacion: {left} * {right} = {result}")
        return result

    def visit_divstatement(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)

        # Verificar que left y right no sean booleanos
        if str(left) == 'True' or str(left) == 'False':
            print(
                f"Error Semantico: El valor izquierdo no puede ser un booleano. Se obtuvo '{left}' de tipo '{type(left).__name__}'.")
            self.semantic_errors.append(
                f"Error Semantico: El valor izquierdo no puede ser un booleano. Se obtuvo '{left}' de tipo '{type(left).__name__}'.")
            return None

        if str(right) == 'True' or str(right) == 'False':
            print(
                f"Error Semantico: El valor derecho no puede ser un booleano. Se obtuvo '{right}' de tipo '{type(right).__name__}'.")
            self.semantic_errors.append(
                f"Error Semantico: El valor derecho no puede ser un booleano. Se obtuvo '{right}' de tipo '{type(right).__name__}'.")
            return None

        if right == 0:
            raise ValueError("Error: Division por cero no permitida.")

        result = left // right
        print(f"Division: {left} // {right} = {result}")
        return result

    def visit_sumstatement(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)

        # Verificar que left y right no sean booleanos
        if str(left) == 'True' or str(left) == 'False':
            print(
                f"Error Semantico: El valor izquierdo no puede ser un booleano. Se obtuvo '{left}' de tipo '{type(left).__name__}'.")
            self.semantic_errors.append(
                f"Error Semantico: El valor izquierdo no puede ser un booleano. Se obtuvo '{left}' de tipo '{type(left).__name__}'.")
            return None

        if str(right) == 'True' or str(right) == 'False':
            print(
                f"Error Semantico: El valor derecho no puede ser un booleano. Se obtuvo '{right}' de tipo '{type(right).__name__}'.")
            self.semantic_errors.append(f"Error Semantico: El valor derecho no puede ser un booleano. Se obtuvo '{right}' de tipo '{type(right).__name__}'.")
            return None

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

        # Inicializar la variable en el contexto
        if self.variable_context.get_variable(node.variable) is not None:
            raise ValueError(f"La variable '{node.variable}' ya existe.")

        # Establecer la variable de control del bucle
        self.variable_context.set_variable(node.variable, min_value, "NUMBER")

        # Ejecutar el cuerpo del bucle
        for i in range(min_value, max_value):
            print(f"Iteracion FOR: {i}")
            # Actualizar el valor de la variable para la iteracion actual
            self.variable_context.set_variable(node.variable, i, "NUMBER")

            # Visitar cada declaracion en el cuerpo del bucle
            for statement in node.body:
                self.visit(statement)

        # Eliminar la variable del contexto al finalizar el bucle
        self.variable_context.remove_variable(node.variable)
    def visit_casestatement(self, node):
        print(f"Ejecutando Case para la variable: {node.variable}")

        # Obtener el valor de la variable
        variable_value = self.variable_context.get_variable(node.variable)
        if variable_value is None:
            raise ValueError(f"La variable '{node.variable}' no esta definida.")

        print(f"Valor de la variable: {variable_value}")

        # Evaluar cada clausula When
        for when_clause in node.when_clauses:
            condition_value = self.visit(when_clause.condition)
            print(f"Evaluando condicion: {condition_value}")

            if condition_value == variable_value:
                print("Condicion cumplida, ejecutando cuerpo del When")
                for statement in when_clause.body:
                    self.visit(statement)
                return

        # Si ninguna condicion se cumple y hay una clausula Else, ejecutarla
        if node.else_clause:
            print("Ninguna condicion cumplida, ejecutando clausula Else")
            for statement in node.else_clause:
                self.visit(statement)
        else:
            print("Ninguna condicion cumplida y no hay clausula Else")

    def visit_repeatstatement(self, node):
        iteration = 0
        while True:
            iteration += 1
            print(f"Iteracion Repeat {iteration}")

            # Ejecutar el cuerpo
            for statement in node.body:
                self.visit(statement)

            # Verificar la condicion
            condition_result = self.visit(node.condition)

            # Asegurarse de que tomamos solo el primer valor si es una lista
            if isinstance(condition_result, list):
                condition_result = condition_result[0]

            print(f"  Resultado de la condicion: {condition_result}")

            if condition_result:
                print("Saliendo del bucle Repeat")
                break  # Salir del bucle si la condicion es verdadera

    def visit_whilestatement(self, node):
        iteration = 0
        while True:
            iteration += 1
            print(f"Iteracion While {iteration}")

            # Evaluar la condicion
            condition_result = self.visit(node.condition)
            print(f"  Resultado de la condicion: {condition_result}")

            # Asegurate de que tomas solo el primer valor si es una lista
            if isinstance(condition_result, list):
                condition_result = condition_result[0]

            if not condition_result:
                print("Saliendo del bucle While")
                break

            # Ejecutar el cuerpo
            for statement in node.body:
                self.visit(statement)

    def visit_procedurestatement(self, node):
        print(f"Ejecutando procedimiento: {node.name}")

        # Ejecutar cada instrucción en el cuerpo del procedimiento
        for statement in node.body:
            self.visit(statement)

    def visit_binaryoperation(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)

        if isinstance(left, list):
            left = left[0]
        if isinstance(right, list):
            right = right[0]

        # Imprimir los valores antes de realizar la operacion
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
                raise ValueError("Division por cero")
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
        # Aqui asumimos que node.expressions es una instancia de ExpressionList
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
                # Si es una cadena, probablemente sea el nombre de un metodo de visita
                method_name = f'visit_{expr.lower()}'
                if hasattr(self, method_name):
                    result = getattr(self, method_name)(expr)
                else:
                    print(f"Error: No se encontro el metodo {method_name}")
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
                print(f"{indent}  {attr}: {value}")  # Si es un valor basico, lo imprime directamente

    def print_symbol_table(self):
        self.variable_context.print_symbol_table()