import random
import re
from writingMachine.ast.add_statement import AddStatement
from writingMachine.ast.and_statement import AndStatement
from writingMachine.ast.beginning_statement import BeginningStatement
from writingMachine.ast.binary_operation import BinaryOperation
from writingMachine.ast.boolean_expression import BooleanExpression
from writingMachine.ast.call_statement import CallStatement
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
from writingMachine.ast.procedure_variable_tracker import ProcedureVariableTracker
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
        self.proc_var_tracker = ProcedureVariableTracker()
        self.x_position = 0
        self.y_position = 0
        self.current_color = 1  # 1 para negro, 2 para rojo
        self.pen_down = False
        self.semantic_errors = []
        self.ast = None

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
        # Guardar el AST completo en la primera visita
        if self.ast is None:
            self.ast = node

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
                                   CaseStatement, WhenClause, ProcedureStatement, CallStatement)):
            return self.visit(node.value)
        return node.value

    def visit_defstatement(self, node):
        var_name = node.var_name
        value = self.visit(node.value)  # Llama a visit para obtener el valor

        # Reglas para el nombre de la variable
        if not re.match(r'^[a-z][a-zA-Z0-9*@]{2,9}$', var_name):
            error_msg = (f"Error Semántico: El nombre de la variable '{var_name}' no cumple "
                         "con las reglas. Debe tener entre 3 y 10 caracteres, comenzar con "
                         "una letra minúscula, y puede contener letras, números, '_' y '@'.")
            print(error_msg)
            self.semantic_errors.append(error_msg)
            return None

        # Determinar el tipo basado en el valor del nodo
        if isinstance(value, bool):
            var_type = "BOOLEAN"
        elif isinstance(value, (int, float)):
            var_type = "NUMBER"
        elif isinstance(node.value, IdExpression):
            var_type = "ID"
        else:
            var_type = "UNKNOWN"

            # Verificar si la variable ya existe en el contexto actual o en Main
        if f"{var_name}_{self.variable_context.current_procedure}" in self.variable_context.variables or \
                f"{var_name}_Main" in self.variable_context.variables:

            # Comprobar el tipo de la variable existente
            existing_var_name = f"{var_name}_{self.variable_context.current_procedure}" \
                if f"{var_name}_{self.variable_context.current_procedure}" in self.variable_context.variables \
                else f"{var_name}_Main"

            existing_type = self.variable_context.get_variable_type(existing_var_name)

            # Verificar si el tipo coincide
            if existing_type != var_type:
                error_msg = (
                    f"Error Semántico: La variable '{existing_var_name}' ya está definida como '{existing_type}', "
                    f"pero se intenta redefinir como '{var_type}'.")
                print(error_msg)
                self.semantic_errors.append(error_msg)
                return None

        # Usar el procedimiento actual al definir la variable
        self.variable_context.set_variable(var_name, value, var_type)
        print(f"Definido {var_name} = {value} (Tipo: {var_type})")
        return value

    def visit_putstatement(self, node):
        var_name = node.var_name
        value = self.visit(node.value)


        # Verificar si la variable está definida en el contexto actual o en Main
        if f"{var_name}_{self.variable_context.current_procedure}" in self.variable_context.variables or \
                f"{var_name}_Main" in self.variable_context.variables:

            # Obtener el nombre de la variable existente
            existing_var_name = f"{var_name}_{self.variable_context.current_procedure}" \
                if f"{var_name}_{self.variable_context.current_procedure}" in self.variable_context.variables \
                else f"{var_name}_Main"

            current_type = self.variable_context.get_variable_type(existing_var_name)

            # Determinar el tipo del nuevo valor
            if isinstance(value, bool):
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
                      f"la variable '{existing_var_name}' que es de tipo '{current_type}'.")
                return None  # O lanza una excepción según tu diseño

            # Si los tipos coinciden, actualiza la variable
            self.variable_context.set_variable(var_name, value, current_type)
            print(f"Actualizado {existing_var_name} = {value}")

        else:
            print(f"Error Semantico: La variable '{var_name}' no esta definida.")
            self.semantic_errors.append(
                f"Error Semantico: La variable '{var_name}' no esta definida.")

    def visit_addstatement(self, node):
        # Verificar si la variable está definida en el contexto actual o en Main
        if f"{node.var_name}_{self.variable_context.current_procedure}" not in self.variable_context.variables and \
                f"{node.var_name}_Main" not in self.variable_context.variables:
            print(f"Error Semantico: '{node.var_name}' no es una variable valida.")
            self.semantic_errors.append(f"Error Semantico: '{node.var_name}' no es una variable valida.")
            return None

        # Obtener el nombre completo de la variable en el contexto actual o en Main
        existing_var_name = f"{node.var_name}_{self.variable_context.current_procedure}" \
            if f"{node.var_name}_{self.variable_context.current_procedure}" in self.variable_context.variables \
            else f"{node.var_name}_Main"

        current_value = self.variable_context.get_variable(existing_var_name)
        current_type = self.variable_context.get_variable_type(existing_var_name)

        # Comprobar si la variable es de tipo numerico
        if current_type != "NUMBER":
            print(f"Error Semantico: No se puede incrementar '{node.var_name}' de tipo '{current_type}'.")
            self.semantic_errors.append(
                f"Error Semantico: No se puede incrementar '{node.var_name}' de tipo '{current_type}'.")
            return None
        # Si no hay un valor de incremento, incrementar por 1
        if node.increment_value is None:
            new_value = current_value + 1
        else:
            # Verificar si la expresión es un ID (nombre de una variable) antes de evaluarla
            if isinstance(node.increment_value.value, IdExpression):
                increment_var_name = node.increment_value.value.var_name  # Obtener el nombre del ID usando var_name
                # Obtener el valor y tipo de la variable del contexto
                if f"{increment_var_name}_{self.variable_context.current_procedure}" in self.variable_context.variables or \
                        f"{increment_var_name}_Main" in self.variable_context.variables:

                    # Obtener valor y tipo de la variable referenciada
                    referenced_var_name = f"{increment_var_name}_{self.variable_context.current_procedure}" \
                        if f"{increment_var_name}_{self.variable_context.current_procedure}" in self.variable_context.variables \
                        else f"{increment_var_name}_Main"
                    referenced_value = self.variable_context.get_variable(referenced_var_name)
                    referenced_type = self.variable_context.get_variable_type(referenced_var_name)

                    # Verificar que el tipo de la variable referenciada sea NUMÉRICO
                    if referenced_type != "NUMBER":
                        print(
                            f"Error Semantico: El incremento debe ser un número, pero '{increment_var_name}' es de tipo '{referenced_type}'.")
                        self.semantic_errors.append(
                            f"Error Semantico: El incremento debe ser un número, pero '{increment_var_name}' es de tipo '{referenced_type}'.")
                        return None

                    # Asignar el valor referenciado como el incremento
                    increment = referenced_value
                else:
                    print(f"Error Semantico: La variable '{increment_var_name}' no está definida.")
                    self.semantic_errors.append(
                        f"Error Semantico: La variable '{increment_var_name}' no está definida.")
                    return None
            else:
                # Si no es un IdExpression, visitar la expresión para evaluarla
                increment = self.visit(node.increment_value)

                # Verificar que el incremento sea un número
                if not isinstance(increment, (int, float)):
                    print(
                        f"Error Semantico: El incremento debe ser un número, pero se obtuvo '{increment}' de tipo '{type(increment).__name__}'.")
                    self.semantic_errors.append(
                        f"Error Semantico: El incremento debe ser un número, pero se obtuvo '{increment}' de tipo '{type(increment).__name__}'.")
                    return None

            # Sumar el incremento
            new_value = current_value + increment

        # Actualizar el valor de la variable
        self.variable_context.set_variable(node.var_name, new_value, current_type)
        print(f"Actualizado {existing_var_name} = {new_value}")

    def visit_continueupstatement(self, node):
        move_units = node.move_units  # No evaluamos aún para verificar si es IdExpression

        # Verificación del tipo de move_units
        if isinstance(move_units.value, IdExpression):
            # Si es un IdExpression, verificar si la variable referenciada está definida
            referenced_var_name = move_units.value.var_name

            if f"{referenced_var_name}_{self.variable_context.current_procedure}" in self.variable_context.variables or \
                    f"{referenced_var_name}_Main" in self.variable_context.variables:
                referenced_full_name = f"{referenced_var_name}_{self.variable_context.current_procedure}" \
                    if f"{referenced_var_name}_{self.variable_context.current_procedure}" in self.variable_context.variables \
                    else f"{referenced_var_name}_Main"

                referenced_value = self.variable_context.get_variable(referenced_full_name)
                if isinstance(referenced_value, (int, float)):
                    self.y_position += referenced_value
                    result = f"Movido {referenced_value} unidades hacia arriba. Nueva posicion en Y: {self.y_position}"
                    print(result)
                    return result
                else:
                    print(f"Error Semantico: No se puede mover '{referenced_value}' unidades. Se esperaba un numero.")
                    self.semantic_errors.append(
                        f"Error Semantico: No se puede mover '{referenced_value}' unidades. Se esperaba un numero.")
                    return None
            else:
                print(f"Error Semantico: La variable '{referenced_var_name}' no está definida.")
                self.semantic_errors.append(f"Error Semantico: La variable '{referenced_var_name}' no está definida.")
                return None
        else:
            # Evaluar el valor directamente
            move_units_value = self.visit(move_units)
            if isinstance(move_units_value, (int, float)):
                self.y_position += move_units_value
                result = f"Movido {move_units_value} unidades hacia arriba. Nueva posicion en Y: {self.y_position}"
                print(result)
                return result
            else:
                print(f"Error Semantico: No se puede mover '{move_units_value}' unidades. Se esperaba un numero.")
                self.semantic_errors.append(
                    f"Error Semantico: No se puede mover '{move_units_value}' unidades. Se esperaba un numero.")
                return None

    def visit_continuedownstatement(self, node):
        move_units = node.move_units

        if isinstance(move_units.value, IdExpression):
            referenced_var_name = move_units.value.var_name
            if f"{referenced_var_name}_{self.variable_context.current_procedure}" in self.variable_context.variables or \
                    f"{referenced_var_name}_Main" in self.variable_context.variables:
                referenced_full_name = f"{referenced_var_name}_{self.variable_context.current_procedure}" \
                    if f"{referenced_var_name}_{self.variable_context.current_procedure}" in self.variable_context.variables \
                    else f"{referenced_var_name}_Main"

                referenced_value = self.variable_context.get_variable(referenced_full_name)
                if isinstance(referenced_value, (int, float)):
                    self.y_position -= referenced_value
                    result = f"Movido {referenced_value} unidades hacia abajo. Nueva posicion en Y: {self.y_position}"
                    print(result)
                    return result
                else:
                    print(f"Error Semantico: No se puede mover '{referenced_value}' unidades. Se esperaba un numero.")
                    self.semantic_errors.append(
                        f"Error Semantico: No se puede mover '{referenced_value}' unidades. Se esperaba un numero.")
                    return None
            else:
                print(f"Error Semantico: La variable '{referenced_var_name}' no está definida.")
                self.semantic_errors.append(f"Error Semantico: La variable '{referenced_var_name}' no está definida.")
                return None
        else:
            move_units_value = self.visit(move_units)
            if isinstance(move_units_value, (int, float)):
                self.y_position -= move_units_value
                result = f"Movido {move_units_value} unidades hacia abajo. Nueva posicion en Y: {self.y_position}"
                print(result)
                return result
            else:
                print(f"Error Semantico: No se puede mover '{move_units_value}' unidades. Se esperaba un numero.")
                self.semantic_errors.append(
                    f"Error Semantico: No se puede mover '{move_units_value}' unidades. Se esperaba un numero.")
                return None

    def visit_continuerightstatement(self, node):
        move_units = node.move_units

        if isinstance(move_units.value, IdExpression):
            referenced_var_name = move_units.value.var_name
            if f"{referenced_var_name}_{self.variable_context.current_procedure}" in self.variable_context.variables or \
                    f"{referenced_var_name}_Main" in self.variable_context.variables:
                referenced_full_name = f"{referenced_var_name}_{self.variable_context.current_procedure}" \
                    if f"{referenced_var_name}_{self.variable_context.current_procedure}" in self.variable_context.variables \
                    else f"{referenced_var_name}_Main"

                referenced_value = self.variable_context.get_variable(referenced_full_name)
                if isinstance(referenced_value, (int, float)):
                    self.x_position += referenced_value
                    result = f"Movido {referenced_value} unidades hacia la derecha. Nueva posicion en X: {self.x_position}"
                    print(result)
                    return result
                else:
                    print(f"Error Semantico: No se puede mover '{referenced_value}' unidades. Se esperaba un numero.")
                    self.semantic_errors.append(
                        f"Error Semantico: No se puede mover '{referenced_value}' unidades. Se esperaba un numero.")
                    return None
            else:
                print(f"Error Semantico: La variable '{referenced_var_name}' no está definida.")
                self.semantic_errors.append(f"Error Semantico: La variable '{referenced_var_name}' no está definida.")
                return None
        else:
            move_units_value = self.visit(move_units)
            if isinstance(move_units_value, (int, float)):
                self.x_position += move_units_value
                result = f"Movido {move_units_value} unidades hacia la derecha. Nueva posicion en X: {self.x_position}"
                print(result)
                return result
            else:
                print(f"Error Semantico: No se puede mover '{move_units_value}' unidades. Se esperaba un numero.")
                self.semantic_errors.append(
                    f"Error Semantico: No se puede mover '{move_units_value}' unidades. Se esperaba un numero.")
                return None

    def visit_continueleftstatement(self, node):
        move_units = node.move_units

        if isinstance(move_units.value, IdExpression):
            referenced_var_name = move_units.value.var_name
            if f"{referenced_var_name}_{self.variable_context.current_procedure}" in self.variable_context.variables or \
                    f"{referenced_var_name}_Main" in self.variable_context.variables:
                referenced_full_name = f"{referenced_var_name}_{self.variable_context.current_procedure}" \
                    if f"{referenced_var_name}_{self.variable_context.current_procedure}" in self.variable_context.variables \
                    else f"{referenced_var_name}_Main"

                referenced_value = self.variable_context.get_variable(referenced_full_name)
                if isinstance(referenced_value, (int, float)):
                    self.x_position -= referenced_value
                    result = f"Movido {referenced_value} unidades hacia la izquierda. Nueva posicion en X: {self.x_position}"
                    print(result)
                    return result
                else:
                    print(f"Error Semantico: No se puede mover '{referenced_value}' unidades. Se esperaba un numero.")
                    self.semantic_errors.append(
                        f"Error Semantico: No se puede mover '{referenced_value}' unidades. Se esperaba un numero.")
                    return None
            else:
                print(f"Error Semantico: La variable '{referenced_var_name}' no está definida.")
                self.semantic_errors.append(f"Error Semantico: La variable '{referenced_var_name}' no está definida.")
                return None
        else:
            move_units_value = self.visit(move_units)
            if isinstance(move_units_value, (int, float)):
                self.x_position -= move_units_value
                result = f"Movido {move_units_value} unidades hacia la izquierda. Nueva posicion en X: {self.x_position}"
                print(result)
                return result
            else:
                print(f"Error Semantico: No se puede mover '{move_units_value}' unidades. Se esperaba un numero.")
                self.semantic_errors.append(
                    f"Error Semantico: No se puede mover '{move_units_value}' unidades. Se esperaba un numero.")
                return None

    def visit_posstatement(self, node):
        # Obtener valores de X e Y
        x_val = node.x_val
        y_val = node.y_val

        x = self.visit(x_val)
        y = self.visit(y_val)

        # Validar contexto para x_val
        if isinstance(x_val.value, IdExpression):
            referenced_var_name = x_val.value.var_name
            referenced_full_name = (
                f"{referenced_var_name}_{self.variable_context.current_procedure}"
                if f"{referenced_var_name}_{self.variable_context.current_procedure}" in self.variable_context.variables
                else f"{referenced_var_name}_Main"
            )

            if referenced_full_name in self.variable_context.variables:
                x_val = self.variable_context.get_variable(referenced_full_name)
            else:
                print(f"Error Semantico: La variable '{referenced_var_name}' no está definida.")
                self.semantic_errors.append(f"Error Semantico: La variable '{referenced_var_name}' no está definida.")
                return None

        # Validar contexto para y_val
        if isinstance(y_val.value, IdExpression):
            referenced_var_name = y_val.value.var_name
            referenced_full_name = (
                f"{referenced_var_name}_{self.variable_context.current_procedure}"
                if f"{referenced_var_name}_{self.variable_context.current_procedure}" in self.variable_context.variables
                else f"{referenced_var_name}_Main"
            )

            if referenced_full_name in self.variable_context.variables:
                y_val = self.variable_context.get_variable(referenced_full_name)
            else:
                print(f"Error Semantico: La variable '{referenced_var_name}' no está definida.")
                self.semantic_errors.append(f"Error Semantico: La variable '{referenced_var_name}' no está definida.")
                return None

        # Verificación de tipo booleano
        if isinstance(x, bool):
            print(
                f"Error Semantico: La posicion X no puede ser un booleano. Se obtuvo '{x}' de tipo '{type(x_val).__name__}'.")
            self.semantic_errors.append(
                f"Error Semantico: La posicion X no puede ser un booleano. Se obtuvo '{x}' de tipo '{type(x_val).__name__}'.")
            return None

        if isinstance(y, bool):
            print(
                f"Error Semantico: La posicion Y no puede ser un booleano. Se obtuvo '{y}' de tipo '{type(y_val).__name__}'.")
            self.semantic_errors.append(
                f"Error Semantico: La posicion Y no puede ser un booleano. Se obtuvo '{y}' de tipo '{type(y_val).__name__}'.")
            return None

        self.x_position = x_val
        self.y_position = y_val
        result = f"Posicion actualizada a X: {self.x_position}, Y: {self.y_position}"
        print(result)
        return result

    def visit_posxstatement(self, node):
        x_val = node.x_val

        # Evaluar x_val
        x = self.visit(x_val)

        # Validar contexto para x_val
        if isinstance(x_val.value, IdExpression):
            referenced_var_name = x_val.value.var_name
            referenced_full_name = (
                f"{referenced_var_name}_{self.variable_context.current_procedure}"
                if f"{referenced_var_name}_{self.variable_context.current_procedure}" in self.variable_context.variables
                else f"{referenced_var_name}_Main"
            )

            if referenced_full_name in self.variable_context.variables:
                x_val = self.variable_context.get_variable(referenced_full_name)
            else:
                print(f"Error Semantico: La variable '{referenced_var_name}' no está definida.")
                self.semantic_errors.append(f"Error Semantico: La variable '{referenced_var_name}' no está definida.")
                return None

        # Verificación de tipo booleano
        if isinstance(x, bool):
            print(
                f"Error Semantico: La posicion X no puede ser un booleano. Se obtuvo '{x}' de tipo '{type(x).__name__}'.")
            self.semantic_errors.append(
                f"Error Semantico: La posicion X no puede ser un booleano. Se obtuvo '{x}' de tipo '{type(x).__name__}'.")
            return None

        self.x_position = x
        result = f"Posicion actualizada a X: {self.x_position}, Y: {self.y_position}"
        print(result)
        return result

    def visit_posystatement(self, node):
        y_val = node.y_val

        # Evaluar y_val
        y = self.visit(y_val)

        # Validar contexto para y_val
        if isinstance(y_val.value, IdExpression):
            referenced_var_name = y_val.value.var_name
            referenced_full_name = (
                f"{referenced_var_name}_{self.variable_context.current_procedure}"
                if f"{referenced_var_name}_{self.variable_context.current_procedure}" in self.variable_context.variables
                else f"{referenced_var_name}_Main"
            )

            if referenced_full_name in self.variable_context.variables:
                y_val = self.variable_context.get_variable(referenced_full_name)
            else:
                print(f"Error Semantico: La variable '{referenced_var_name}' no está definida.")
                self.semantic_errors.append(f"Error Semantico: La variable '{referenced_var_name}' no está definida.")
                return None

        # Verificación de tipo booleano
        if isinstance(y, bool):
            print(
                f"Error Semantico: La posicion Y no puede ser un booleano. Se obtuvo '{y}' de tipo '{type(y).__name__}'.")
            self.semantic_errors.append(
                f"Error Semantico: La posicion Y no puede ser un booleano. Se obtuvo '{y}' de tipo '{type(y).__name__}'.")
            return None

        self.y_position = y
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

        # Verificación de contexto para left
        if isinstance(node.left.value, IdExpression):
            referenced_var_name = node.left.value.var_name
            referenced_full_name = (
                f"{referenced_var_name}_{self.variable_context.current_procedure}"
                if f"{referenced_var_name}_{self.variable_context.current_procedure}" in self.variable_context.variables
                else f"{referenced_var_name}_Main"
            )

            if referenced_full_name not in self.variable_context.variables:
                print(f"Error Semantico: La variable '{referenced_var_name}' no está definida.")
                self.semantic_errors.append(f"Error Semantico: La variable '{referenced_var_name}' no está definida.")
                return None

        # Verificación de contexto para right
        if isinstance(node.right.value, IdExpression):
            referenced_var_name = node.right.value.var_name
            referenced_full_name = (
                f"{referenced_var_name}_{self.variable_context.current_procedure}"
                if f"{referenced_var_name}_{self.variable_context.current_procedure}" in self.variable_context.variables
                else f"{referenced_var_name}_Main"
            )

            if referenced_full_name not in self.variable_context.variables:
                print(f"Error Semantico: La variable '{referenced_var_name}' no está definida.")
                self.semantic_errors.append(f"Error Semantico: La variable '{referenced_var_name}' no está definida.")
                return None

        result = left == right
        print(result)
        return result

    def visit_andstatement(self, node):
        left = node.left.accept(self)
        right = node.right.accept(self)

        # Verificación de contexto para left
        if isinstance(node.left.value, IdExpression):
            referenced_var_name = node.left.value.var_name
            referenced_full_name = (
                f"{referenced_var_name}_{self.variable_context.current_procedure}"
                if f"{referenced_var_name}_{self.variable_context.current_procedure}" in self.variable_context.variables
                else f"{referenced_var_name}_Main"
            )

            if referenced_full_name not in self.variable_context.variables:
                print(f"Error Semantico: La variable '{referenced_var_name}' no está definida.")
                self.semantic_errors.append(f"Error Semantico: La variable '{referenced_var_name}' no está definida.")
                return None

        # Verificación de contexto para right
        if isinstance(node.right.value, IdExpression):
            referenced_var_name = node.right.value.var_name
            referenced_full_name = (
                f"{referenced_var_name}_{self.variable_context.current_procedure}"
                if f"{referenced_var_name}_{self.variable_context.current_procedure}" in self.variable_context.variables
                else f"{referenced_var_name}_Main"
            )

            if referenced_full_name not in self.variable_context.variables:
                print(f"Error Semantico: La variable '{referenced_var_name}' no está definida.")
                self.semantic_errors.append(f"Error Semantico: La variable '{referenced_var_name}' no está definida.")
                return None

        result = bool(left) and bool(right)
        print(result)
        return result

    def visit_orstatement(self, node):
        left = node.left.accept(self)
        right = node.right.accept(self)

        # Verificación de contexto para left
        if isinstance(node.left.value, IdExpression):
            referenced_var_name = node.left.value.var_name
            referenced_full_name = (
                f"{referenced_var_name}_{self.variable_context.current_procedure}"
                if f"{referenced_var_name}_{self.variable_context.current_procedure}" in self.variable_context.variables
                else f"{referenced_var_name}_Main"
            )

            if referenced_full_name not in self.variable_context.variables:
                print(f"Error Semantico: La variable '{referenced_var_name}' no está definida.")
                self.semantic_errors.append(f"Error Semantico: La variable '{referenced_var_name}' no está definida.")
                return None

        # Verificación de contexto para right
        if isinstance(node.right.value, IdExpression):
            referenced_var_name = node.right.value.var_name
            referenced_full_name = (
                f"{referenced_var_name}_{self.variable_context.current_procedure}"
                if f"{referenced_var_name}_{self.variable_context.current_procedure}" in self.variable_context.variables
                else f"{referenced_var_name}_Main"
            )

            if referenced_full_name not in self.variable_context.variables:
                print(f"Error Semantico: La variable '{referenced_var_name}' no está definida.")
                self.semantic_errors.append(f"Error Semantico: La variable '{referenced_var_name}' no está definida.")
                return None

        result = bool(left) or bool(right)
        print(result)
        return result

    def visit_greaterstatement(self, node):
        left = node.left.accept(self)
        right = node.right.accept(self)

        # Verificación de contexto para left
        if isinstance(node.left.value, IdExpression):
            referenced_var_name = node.left.value.var_name
            referenced_full_name = (
                f"{referenced_var_name}_{self.variable_context.current_procedure}"
                if f"{referenced_var_name}_{self.variable_context.current_procedure}" in self.variable_context.variables
                else f"{referenced_var_name}_Main"
            )

            if referenced_full_name not in self.variable_context.variables:
                print(f"Error Semantico: La variable '{referenced_var_name}' no está definida.")
                self.semantic_errors.append(f"Error Semantico: La variable '{referenced_var_name}' no está definida.")
                return None

        # Verificación de contexto para right
        if isinstance(node.right.value, IdExpression):
            referenced_var_name = node.right.value.var_name
            referenced_full_name = (
                f"{referenced_var_name}_{self.variable_context.current_procedure}"
                if f"{referenced_var_name}_{self.variable_context.current_procedure}" in self.variable_context.variables
                else f"{referenced_var_name}_Main"
            )

            if referenced_full_name not in self.variable_context.variables:
                print(f"Error Semantico: La variable '{referenced_var_name}' no está definida.")
                self.semantic_errors.append(f"Error Semantico: La variable '{referenced_var_name}' no está definida.")
                return None

        # Verificar que left y right no sean booleanos
        if isinstance(left, bool):
            print(
                f"Error Semantico: El valor izquierdo no puede ser un booleano. Se obtuvo '{left}' de tipo '{type(left).__name__}'.")
            self.semantic_errors.append(
                f"Error Semantico: El valor izquierdo no puede ser un booleano. Se obtuvo '{left}' de tipo '{type(left).__name__}'.")
            return None

        if isinstance(right, bool):
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

        # Verificación de contexto para left
        if isinstance(node.left.value, IdExpression):
            referenced_var_name = node.left.value.var_name
            referenced_full_name = (
                f"{referenced_var_name}_{self.variable_context.current_procedure}"
                if f"{referenced_var_name}_{self.variable_context.current_procedure}" in self.variable_context.variables
                else f"{referenced_var_name}_Main"
            )

            if referenced_full_name not in self.variable_context.variables:
                print(f"Error Semantico: La variable '{referenced_var_name}' no está definida.")
                self.semantic_errors.append(f"Error Semantico: La variable '{referenced_var_name}' no está definida.")
                return None

        # Verificación de contexto para right
        if isinstance(node.right.value, IdExpression):
            referenced_var_name = node.right.value.var_name
            referenced_full_name = (
                f"{referenced_var_name}_{self.variable_context.current_procedure}"
                if f"{referenced_var_name}_{self.variable_context.current_procedure}" in self.variable_context.variables
                else f"{referenced_var_name}_Main"
            )

            if referenced_full_name not in self.variable_context.variables:
                print(f"Error Semantico: La variable '{referenced_var_name}' no está definida.")
                self.semantic_errors.append(f"Error Semantico: La variable '{referenced_var_name}' no está definida.")
                return None

        # Verificar que left y right no sean booleanos
        if isinstance(left, bool):
            print(
                f"Error Semantico: El valor izquierdo no puede ser un booleano. Se obtuvo '{left}' de tipo '{type(left).__name__}'.")
            self.semantic_errors.append(
                f"Error Semantico: El valor izquierdo no puede ser un booleano. Se obtuvo '{left}' de tipo '{type(left).__name__}'.")
            return None

        if isinstance(right, bool):
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

        # Verificación de contexto para left
        if isinstance(node.left.value, IdExpression):
            referenced_var_name = node.left.value.var_name
            referenced_full_name = (
                f"{referenced_var_name}_{self.variable_context.current_procedure}"
                if f"{referenced_var_name}_{self.variable_context.current_procedure}" in self.variable_context.variables
                else f"{referenced_var_name}_Main"
            )

            if referenced_full_name not in self.variable_context.variables:
                print(f"Error Semantico: La variable '{referenced_var_name}' no está definida.")
                self.semantic_errors.append(f"Error Semantico: La variable '{referenced_var_name}' no está definida.")
                return None

        # Verificación de contexto para right
        if isinstance(node.right.value, IdExpression):
            referenced_var_name = node.right.value.var_name
            referenced_full_name = (
                f"{referenced_var_name}_{self.variable_context.current_procedure}"
                if f"{referenced_var_name}_{self.variable_context.current_procedure}" in self.variable_context.variables
                else f"{referenced_var_name}_Main"
            )

            if referenced_full_name not in self.variable_context.variables:
                print(f"Error Semantico: La variable '{referenced_var_name}' no está definida.")
                self.semantic_errors.append(f"Error Semantico: La variable '{referenced_var_name}' no está definida.")
                return None

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
            print(
                f"Error Semantico: N1 debe ser mayor o igual a N2.")
            self.semantic_errors.append(
                f"Error Semantico: N1 debe ser mayor o igual a N2.")
            return None
        result = left - right
        print(f"Sustraccion: {left} - {right} = {result}")
        return result

    def visit_randomstatement(self, node):
        # Obtener el valor de n
        n = node.value.accept(self)  # Asegúrate de que node.value sea un nodo que pueda ser evaluado
        # Verificación de contexto para n
        if isinstance(node.value.value, IdExpression):
            referenced_var_name = node.value.value.var_name
            referenced_full_name = (
                f"{referenced_var_name}_{self.variable_context.current_procedure}"
                if f"{referenced_var_name}_{self.variable_context.current_procedure}" in self.variable_context.variables
                else f"{referenced_var_name}_Main"
            )

            if referenced_full_name not in self.variable_context.variables:
                print(f"Error Semantico: La variable '{referenced_var_name}' no está definida.")
                self.semantic_errors.append(f"Error Semantico: La variable '{referenced_var_name}' no está definida.")
                return None

        # Verificar que n no sea un booleano
        if str(n) == 'True' or str(n) == 'False':
            print(f"Error Semantico: n no puede ser un booleano. Se obtuvo '{n}' de tipo '{type(n).__name__}'.")
            self.semantic_errors.append(
                f"Error Semantico: n no puede ser un booleano. Se obtuvo '{n}' de tipo '{type(n).__name__}'.")
            return None

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

        # Verificación de contexto para left
        if isinstance(node.left.value, IdExpression):
            referenced_var_name = node.left.value.var_name
            referenced_full_name = (
                f"{referenced_var_name}_{self.variable_context.current_procedure}"
                if f"{referenced_var_name}_{self.variable_context.current_procedure}" in self.variable_context.variables
                else f"{referenced_var_name}_Main"
            )

            if referenced_full_name not in self.variable_context.variables:
                print(f"Error Semantico: La variable '{referenced_var_name}' no está definida.")
                self.semantic_errors.append(f"Error Semantico: La variable '{referenced_var_name}' no está definida.")
                return None

        # Verificación de contexto para right
        if isinstance(node.right.value, IdExpression):
            referenced_var_name = node.right.value.var_name
            referenced_full_name = (
                f"{referenced_var_name}_{self.variable_context.current_procedure}"
                if f"{referenced_var_name}_{self.variable_context.current_procedure}" in self.variable_context.variables
                else f"{referenced_var_name}_Main"
            )

            if referenced_full_name not in self.variable_context.variables:
                print(f"Error Semantico: La variable '{referenced_var_name}' no está definida.")
                self.semantic_errors.append(f"Error Semantico: La variable '{referenced_var_name}' no está definida.")
                return None

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

        # Verificación de contexto para left
        if isinstance(node.left.value, IdExpression):
            referenced_var_name = node.left.value.var_name
            referenced_full_name = (
                f"{referenced_var_name}_{self.variable_context.current_procedure}"
                if f"{referenced_var_name}_{self.variable_context.current_procedure}" in self.variable_context.variables
                else f"{referenced_var_name}_Main"
            )

            if referenced_full_name not in self.variable_context.variables:
                print(f"Error Semantico: La variable '{referenced_var_name}' no está definida.")
                self.semantic_errors.append(f"Error Semantico: La variable '{referenced_var_name}' no está definida.")
                return None

        # Verificación de contexto para right
        if isinstance(node.right.value, IdExpression):
            referenced_var_name = node.right.value.var_name
            referenced_full_name = (
                f"{referenced_var_name}_{self.variable_context.current_procedure}"
                if f"{referenced_var_name}_{self.variable_context.current_procedure}" in self.variable_context.variables
                else f"{referenced_var_name}_Main"
            )

            if referenced_full_name not in self.variable_context.variables:
                print(f"Error Semantico: La variable '{referenced_var_name}' no está definida.")
                self.semantic_errors.append(f"Error Semantico: La variable '{referenced_var_name}' no está definida.")
                return None

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
            print(
                f"Error Semantico: Division por cero.")
            self.semantic_errors.append(
                f"Error Semantico: Division por cero.")
            return None
        result = left // right
        print(f"Division: {left} // {right} = {result}")
        return result

    def visit_sumstatement(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)

        # Verificación de contexto para left
        if isinstance(node.left.value, IdExpression):
            referenced_var_name = node.left.value.var_name
            referenced_full_name = (
                f"{referenced_var_name}_{self.variable_context.current_procedure}"
                if f"{referenced_var_name}_{self.variable_context.current_procedure}" in self.variable_context.variables
                else f"{referenced_var_name}_Main"
            )

            if referenced_full_name not in self.variable_context.variables:
                print(f"Error Semantico: La variable '{referenced_var_name}' no está definida.")
                self.semantic_errors.append(f"Error Semantico: La variable '{referenced_var_name}' no está definida.")
                return None

        # Verificación de contexto para right
        if isinstance(node.right.value, IdExpression):
            referenced_var_name = node.right.value.var_name
            referenced_full_name = (
                f"{referenced_var_name}_{self.variable_context.current_procedure}"
                if f"{referenced_var_name}_{self.variable_context.current_procedure}" in self.variable_context.variables
                else f"{referenced_var_name}_Main"
            )

            if referenced_full_name not in self.variable_context.variables:
                print(f"Error Semantico: La variable '{referenced_var_name}' no está definida.")
                self.semantic_errors.append(f"Error Semantico: La variable '{referenced_var_name}' no está definida.")
                return None

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

        result = left + right
        print(f"Suma: {left} + {right} = {result}")
        return result

    def visit_forstatement(self, node):
        # Obtener los valores de min_value y max_value
        min_value = self.visit(node.min_value)
        max_value = self.visit(node.max_value)
        print(min_value)

        # Verificar que min_value y max_value sean enteros
        if not isinstance(min_value, int):
            error_msg = f"Error Semántico: min_value debe ser un número entero. Se obtuvo '{min_value}' de tipo '{type(min_value).__name__}'."
            print(error_msg)
            self.semantic_errors.append(error_msg)
            return None

        if not isinstance(max_value, int):
            error_msg = f"Error Semántico: max_value debe ser un número entero. Se obtuvo '{max_value}' de tipo '{type(max_value).__name__}'."
            print(error_msg)
            self.semantic_errors.append(error_msg)
            return None

        # Verificar si min_value es mayor o igual que max_value
        if min_value >= max_value:
            raise ValueError("Max debe ser mayor que Min en el bucle FOR.")

        # Reglas para el nombre de la variable de control
        if not re.match(r'^[a-z][a-zA-Z0-9*@]{2,9}$', node.variable):
            error_msg = (f"Error Semántico: El nombre de la variable de control '{node.variable}' no cumple "
                         "con las reglas. Debe tener entre 3 y 10 caracteres, comenzar con "
                         "una letra minúscula, y puede contener letras, números, '_' y '@'.")
            print(error_msg)
            self.semantic_errors.append(error_msg)
            return None

        # Verificar si la variable ya existe en el contexto actual o en global
        if f"{node.variable}_{self.variable_context.current_procedure}" in self.variable_context.variables or \
                f"{node.variable}_Main" in self.variable_context.variables:
            error_msg = f"La variable '{node.variable}' ya existe en el contexto actual o global."
            print(error_msg)
            self.semantic_errors.append(error_msg)
            return None

        # Inicializar la variable en el contexto
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

        # Verificación de contexto para la variable que se está evaluando

        referenced_var_name = node.variable
        referenced_full_name = (
            f"{referenced_var_name}_{self.variable_context.current_procedure}"
            if f"{referenced_var_name}_{self.variable_context.current_procedure}" in self.variable_context.variables
            else f"{referenced_var_name}_Main"
        )

        if referenced_full_name not in self.variable_context.variables:
            print(f"Error Semantico: La variable '{referenced_var_name}' no está definida.")
            self.semantic_errors.append(f"Error Semantico: La variable '{referenced_var_name}' no está definida.")
            return None

        # Obtener el valor de la variable
        variable_value = self.variable_context.get_variable(node.variable)
        print(f"Valor de la variable: {variable_value}")

        # Evaluar cada cláusula When
        for when_clause in node.when_clauses:
            condition_value = self.visit(when_clause.condition)
            print(f"Evaluando condición: {condition_value}")

            if condition_value == variable_value:
                print("Condición cumplida, ejecutando cuerpo del When")
                for statement in when_clause.body:
                    self.visit(statement)
                return

        # Si ninguna condición se cumple y hay una cláusula Else, ejecutarla
        if node.else_clause:
            print("Ninguna condición cumplida, ejecutando cláusula Else")
            for statement in node.else_clause:
                self.visit(statement)
        else:
            print("Ninguna condición cumplida y no hay cláusula Else")

    def visit_repeatstatement(self, node):
        iteration = 0
        while True:
            iteration += 1
            print(f"Iteracion Repeat {iteration}")

            # Ejecutar el cuerpo
            for statement in node.body:
                self.visit(statement)

            # Verificar la condición
            condition_result = self.visit(node.condition)

            # Asegurarse de que tomamos solo el primer valor si es una lista
            if isinstance(condition_result, list):
                condition_result = condition_result[0]



            # Verificación de contexto para la variable en la condición
            if isinstance(node.condition, IdExpression):
                referenced_var_name = node.condition.var_name
                referenced_full_name = (
                    f"{referenced_var_name}_{self.variable_context.current_procedure}"
                    if f"{referenced_var_name}_{self.variable_context.current_procedure}" in self.variable_context.variables
                    else f"{referenced_var_name}_Main"
                )

                if referenced_full_name not in self.variable_context.variables:
                    print(f"Error Semantico: La variable '{referenced_var_name}' no está definida.")
                    self.semantic_errors.append(
                        f"Error Semantico: La variable '{referenced_var_name}' no está definida.")
                    return None  # Detener la ejecución del método si la variable no está definida

            # Verificar si el resultado de la condición es None
            if condition_result is None:
                break  # Salir del bucle si el resultado de la condición es None

            print(f"  Resultado de la condicion: {condition_result}")

            if condition_result:
                print("Saliendo del bucle Repeat")
                break  # Salir del bucle si la condición es verdadera

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
        print(f"Registrando procedimiento: {node.name}")

        # Extraer los nombres de los parámetros
        parameters = []
        for param in node.parameters:
            if isinstance(param, IdExpression):
                parameters.append(param.var_name)
            else:
                parameters.append(str(param))

        param_count = len(parameters)

        # Verificar si ya existe un procedimiento con el mismo nombre y cantidad de parámetros
        if self.proc_var_tracker.get_procedure(node.name, param_count):
            error_msg = (f"Error Semántico: El procedimiento '{node.name}' ya está definido "
                         f"con {param_count} parámetros.")
            print(error_msg)
            self.semantic_errors.append(error_msg)
            return None  # Salir si ya existe un procedimiento con el mismo nombre y número de parámetros

        # Registrar el procedimiento en el tracker
        self.proc_var_tracker.register_procedure(node.name, parameters)

        print(f"Procedimiento {node.name} registrado con {param_count} parámetros: {parameters}")

    def visit_callstatement(self, node):
        procedure_name = node.procedure_name
        param_count = len(node.arguments)
        self.current_procedure = node.procedure_name
        self.variable_context.set_current_procedure(node.procedure_name)

        print(f"\nEjecutando llamada al procedimiento: {procedure_name} con {param_count} argumentos")

        # Verificar si existe un procedimiento con el nombre y cantidad de parámetros
        proc_info = self.proc_var_tracker.get_procedure(procedure_name, param_count)

        if proc_info is None:
            error_msg = (f"Error Semántico: El procedimiento '{procedure_name}' no está definido "
                         f"con {param_count} parámetros.")
            print(error_msg)
            self.semantic_errors.append(error_msg)
            return None

        expected_params = proc_info["params"]

        # Verificar el número de argumentos
        if len(node.arguments) != len(expected_params):
            error_msg = (
                f"Error Semántico: El procedimiento '{procedure_name}' espera {len(expected_params)} parámetros, "
                f"pero se proporcionaron {len(node.arguments)}.")
            print(error_msg)
            self.semantic_errors.append(error_msg)
            return None

        # Evaluar y asignar los argumentos a los parámetros
        for param_name, arg in zip(expected_params, node.arguments):
            if isinstance(arg, IdExpression):
                # Si el argumento es una variable, obtener su valor del contexto
                arg_value = self.variable_context.get_variable(arg.var_name)
                if arg_value is None:
                    error_msg = f"Error Semántico: La variable '{arg.var_name}' no está definida."
                    print(error_msg)
                    self.semantic_errors.append(error_msg)
                    return None
                value = arg_value
            else:
                # Si es un valor directo, evaluarlo
                value = self.visit(arg)

            print(f"Asignando parámetro {param_name} = {value}")

            # Determinar el tipo del valor
            if isinstance(value, bool):
                var_type = "BOOLEAN"
            elif isinstance(value, (int, float)):
                var_type = "NUMBER"
            else:
                var_type = "UNKNOWN"

            # Asignar el valor al parámetro en el contexto con su tipo
            self.variable_context.set_variable(param_name, value, var_type)

        # Buscar y ejecutar el cuerpo del procedimiento
        for stmt in self.ast.statements:
            if isinstance(stmt, ProcedureStatement) and stmt.name == procedure_name and len(
                    stmt.parameters) == param_count:
                print(f"Ejecutando cuerpo del procedimiento {procedure_name}")
                # Ejecutar cada statement en el cuerpo del procedimiento
                for statement in stmt.body[0].statements:  # Nota el [0] aquí
                    self.visit(statement)
                break

        # Limpiar el procedimiento actual después de la ejecución
        self.variable_context.clear_current_procedure()
        print(f"Finalizada la ejecución del procedimiento {procedure_name}\n")

    def visit_binaryoperation(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)

        if isinstance(left, list):
            left = left[0]
        if isinstance(right, list):
            right = right[0]

        # Imprimir los valores antes de realizar la operación
        print(f"Operando izquierdo: {left}, Operando derecho: {right}, Operador: {node.operator}")

        # Verificar que ambos operandos son del mismo tipo
        if type(left) != type(right):
            print(f"Error Semantico: Los operandos deben ser del mismo tipo. "
                  f"Encontrado {type(left).__name__} y {type(right).__name__}.")
            self.semantic_errors.append(f"Error Semantico: Los operandos deben ser del mismo tipo. "
                                        f"Encontrado {type(left).__name__} y {type(right).__name__}.")
            return None

        # Verificación del contexto para left
        if isinstance(node.left, IdExpression):
            referenced_var_name = node.left.var_name
            referenced_full_name = (
                f"{referenced_var_name}_{self.variable_context.current_procedure}"
                if f"{referenced_var_name}_{self.variable_context.current_procedure}" in self.variable_context.variables
                else f"{referenced_var_name}_Main"
            )

            if referenced_full_name not in self.variable_context.variables:
                print(f"Error Semantico: La variable '{referenced_var_name}' no está definida.")
                self.semantic_errors.append(f"Error Semantico: La variable '{referenced_var_name}' no está definida.")
                return None

        # Verificación del contexto para right
        if isinstance(node.right, IdExpression):
            referenced_var_name = node.right.var_name
            referenced_full_name = (
                f"{referenced_var_name}_{self.variable_context.current_procedure}"
                if f"{referenced_var_name}_{self.variable_context.current_procedure}" in self.variable_context.variables
                else f"{referenced_var_name}_Main"
            )

            if referenced_full_name not in self.variable_context.variables:
                print(f"Error Semantico: La variable '{referenced_var_name}' no está definida.")
                self.semantic_errors.append(f"Error Semantico: La variable '{referenced_var_name}' no está definida.")
                return None

        # Operaciones
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
                print("Error Semantico: Division por cero")
                self.semantic_errors.append("Error Semantico: Division por cero")
                return None
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

    def print_procedure_tracker(self):
        self.proc_var_tracker.print_summary()