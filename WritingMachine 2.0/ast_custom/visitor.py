import random
import re
from ast_custom.add_statement import AddStatement
from ast_custom.and_statement import AndStatement
from ast_custom.beginning_statement import BeginningStatement
from ast_custom.binary_operation import BinaryOperation
from ast_custom.boolean_expression import BooleanExpression
from ast_custom.call_statement import CallStatement
from ast_custom.case_statement import CaseStatement
from ast_custom.continuedown_statement import ContinueDownStatement
from ast_custom.continueleft_statement import ContinueLeftStatement
from ast_custom.continueright_statement import ContinueRightStatement
from ast_custom.continueup_statement import ContinueUpStatement
from ast_custom.def_statement import DefStatement
from ast_custom.div_statement import DivStatement
from ast_custom.down_statement import DownStatement
from ast_custom.equal_statement import EqualStatement
from ast_custom.execute_statement import ExecuteStatement
from ast_custom.expression_bracket import ExpressionBracket
from ast_custom.expression_group import ExpressionGroup
from ast_custom.expression_list import ExpressionList
from ast_custom.for_statement import ForStatement
from ast_custom.greater_statement import GreaterStatement
from ast_custom.id_expression import IdExpression
from ast_custom.mult_statement import MultStatement
from ast_custom.node import ASTNode
from ast_custom.number_expression import NumberExpression
from ast_custom.or_statement import OrStatement
from ast_custom.pos_statement import PosStatement
from ast_custom.posx_statement import PosXStatement
from ast_custom.posy_statement import PosYStatement
from ast_custom.procedure_statement import ProcedureStatement
from ast_custom.procedure_variable_tracker import ProcedureVariableTracker
from ast_custom.put_statement import PutStatement
from ast_custom.random_statement import RandomStatement
from ast_custom.repeat_statement import RepeatStatement
from ast_custom.smaller_statement import SmallerStatement
from ast_custom.substr_statement import SubstrStatement
from ast_custom.sum_statement import SumStatement
from ast_custom.turnleft_statement import TurnLeftStatement
from ast_custom.turnright_statement import TurnRightStatement
from ast_custom.up_statement import UpStatement
from ast_custom.usecolor_statement import UseColorStatement
from ast_custom.variable_context import VariableContext
from ast_custom.when_clause import WhenClause
from ast_custom.while_statement import WhileStatement
from llvmlite import ir, binding

class ASTVisitor:
    """Clase base para visitar los nodos del AST."""

    def __init__(self):
        self.module = ir.Module(name="modulo_principal")
        self.builder = None
        self.symbol_table = {}
        self.variable_context = VariableContext()
        self.proc_var_tracker = ProcedureVariableTracker()
        self.x_position = 0
        self.y_position = 0
        self.angle = 0
        self.current_color = 1  # 1 para negro, 2 para rojo
        self.pen_down = False
        self.semantic_errors = []
        self.ast = None

        # Crear variables globales x_position, y_position y pen_down
        self.global_vars = {
            "x_position": ir.GlobalVariable(self.module, ir.IntType(32), name="x_position"),
            "y_position": ir.GlobalVariable(self.module, ir.IntType(32), name="y_position"),
            "pen_down": ir.GlobalVariable(self.module, ir.IntType(1), name="pen_down"),
        }

        # Inicializar variables globales con valores predeterminados
        self.global_vars["x_position"].initializer = ir.Constant(ir.IntType(32), 0)
        self.global_vars["y_position"].initializer = ir.Constant(ir.IntType(32), 0)
        self.global_vars["pen_down"].initializer = ir.Constant(ir.IntType(1), 0)

        # Especificar que las variables globales son modificables
        for var in self.global_vars.values():
            var.linkage = "common"
            var.global_constant = False



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
                                   CaseStatement, WhenClause, ProcedureStatement, CallStatement, TurnRightStatement, TurnLeftStatement)):
            return self.visit(node.value)
        return node.value

    def visit_defstatement(self, node):
        var_name = node.var_name
        value = self.visit(node.value)  # Llama a visit para obtener el valor
        alloca = None  # Declaramos aquí para usarlo en cualquier caso

        # Crear espacio para la variable en la pila según el tipo
        if isinstance(value, bool):
            alloca = self.builder.alloca(ir.IntType(1), name=var_name)  # Asignar 1 bit para booleanos
        elif isinstance(value, (int, float)):
            alloca = self.builder.alloca(ir.IntType(32), name=var_name)  # Asignar 32 bits para números
        else:
            error_msg = f"Error Semántico: Tipo de dato no reconocido para la variable '{var_name}'."
            print(error_msg)
            self.semantic_errors.append(error_msg)
            return None

        self.symbol_table[var_name] = alloca  # Guardar referencia en la tabla de símbolos

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
            constant = ir.Constant(ir.IntType(1), int(value))  # Convertir True/False a 1/0
            self.builder.store(constant, alloca)  # Almacenar el valor booleano
            var_type = "BOOLEAN"
        elif isinstance(value, (int, float)):
            constant = ir.Constant(ir.IntType(32), value)
            self.builder.store(constant, alloca)
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
            alloca = self.symbol_table[var_name]
            current_type = self.variable_context.get_variable_type(existing_var_name)

            # Determinar el tipo del nuevo valor
            if isinstance(value, bool):
                new_type = "BOOLEAN"
                constant = ir.Constant(ir.IntType(1), int(value))  # Convertir True/False a 1/0

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
        var_name = node.var_name

        # Verificar si la variable está definida en el contexto actual o en Main
        if f"{var_name}_{self.variable_context.current_procedure}" not in self.variable_context.variables and \
                f"{var_name}_Main" not in self.variable_context.variables:
            error_msg = f"Error Semantico: '{var_name}' no es una variable valida."
            print(error_msg)
            self.semantic_errors.append(error_msg)
            return None

        # Obtener el nombre completo de la variable en el contexto actual o en Main
        existing_var_name = f"{var_name}_{self.variable_context.current_procedure}" \
            if f"{var_name}_{self.variable_context.current_procedure}" in self.variable_context.variables \
            else f"{var_name}_Main"

        current_value = self.variable_context.get_variable(existing_var_name)
        current_type = self.variable_context.get_variable_type(existing_var_name)

        # Comprobar si la variable es de tipo numerico
        if current_type != "NUMBER":
            error_msg = f"Error Semantico: No se puede incrementar '{var_name}' de tipo '{current_type}'."
            print(error_msg)
            self.semantic_errors.append(error_msg)
            return None

        # Obtener el alloca de la tabla de símbolos
        alloca = self.symbol_table[var_name]

        # Si no hay un valor de incremento, incrementar por 1
        if node.increment_value is None:
            increment_value = 1
            new_value = current_value + 1
        else:
            # Verificar si la expresión es un ID (nombre de una variable)
            if isinstance(node.increment_value.value, IdExpression):
                increment_var_name = node.increment_value.value.var_name

                if f"{increment_var_name}_{self.variable_context.current_procedure}" in self.variable_context.variables or \
                        f"{increment_var_name}_Main" in self.variable_context.variables:

                    referenced_var_name = f"{increment_var_name}_{self.variable_context.current_procedure}" \
                        if f"{increment_var_name}_{self.variable_context.current_procedure}" in self.variable_context.variables \
                        else f"{increment_var_name}_Main"

                    referenced_value = self.variable_context.get_variable(referenced_var_name)
                    referenced_type = self.variable_context.get_variable_type(referenced_var_name)

                    if referenced_type != "NUMBER":
                        error_msg = f"Error Semantico: El incremento debe ser un número, pero '{increment_var_name}' es de tipo '{referenced_type}'."
                        print(error_msg)
                        self.semantic_errors.append(error_msg)
                        return None

                    increment_value = referenced_value
                    new_value = current_value + increment_value
                else:
                    error_msg = f"Error Semantico: La variable '{increment_var_name}' no está definida."
                    print(error_msg)
                    self.semantic_errors.append(error_msg)
                    return None
            else:
                increment_value = self.visit(node.increment_value)

                if not isinstance(increment_value, (int, float)):
                    error_msg = f"Error Semantico: El incremento debe ser un número, pero se obtuvo '{increment_value}' de tipo '{type(increment_value).__name__}'."
                    print(error_msg)
                    self.semantic_errors.append(error_msg)
                    return None

                new_value = current_value + increment_value

        # Crear la constante LLVM para el nuevo valor
        constant = ir.Constant(ir.IntType(32), new_value)

        # Almacenar el nuevo valor en la variable
        self.builder.store(constant, alloca)

        # Actualizar el valor en el contexto de variables
        self.variable_context.set_variable(var_name, new_value, current_type)
        print(f"Actualizado {existing_var_name} = {new_value}")

        return new_value

    def visit_continueupstatement(self, node):
        move_units = node.move_units

        # Obtener la variable global y_position y asegurarse de que esté correctamente declarada
        y_pos_global = self.global_vars["y_position"]
        y_pos_global.linkage = "common"  # Asegurar que es visible externamente
        y_pos_global.global_constant = False

        if not hasattr(y_pos_global, 'initializer') or y_pos_global.initializer is None:
            y_pos_global.initializer = ir.Constant(ir.IntType(32), 0)

        # Verificación del tipo de move_units
        if isinstance(move_units.value, IdExpression):
            referenced_var_name = move_units.value.var_name

            if f"{referenced_var_name}_{self.variable_context.current_procedure}" in self.variable_context.variables or \
                    f"{referenced_var_name}_Main" in self.variable_context.variables:
                referenced_full_name = f"{referenced_var_name}_{self.variable_context.current_procedure}" \
                    if f"{referenced_var_name}_{self.variable_context.current_procedure}" in self.variable_context.variables \
                    else f"{referenced_var_name}_Main"

                referenced_value = self.variable_context.get_variable(referenced_full_name)

                if isinstance(referenced_value, bool):
                    error_msg = f"Error Semantico: No se puede mover '{referenced_value}' unidades. Se esperaba un numero."
                    print(error_msg)
                    self.semantic_errors.append(error_msg)
                    return None

                if isinstance(referenced_value, (int, float)):
                    # Si la variable referenciada está en la tabla de símbolos
                    if referenced_var_name in self.symbol_table:
                        # Cargar el valor de la variable referenciada
                        move_value_ptr = self.symbol_table[referenced_var_name]
                        move_amount = self.builder.load(move_value_ptr)
                    else:
                        # Si no está en la tabla de símbolos, usar el valor directamente
                        move_amount = ir.Constant(ir.IntType(32), int(referenced_value))

                    # Cargar el valor actual de y_position
                    current_y = self.builder.load(y_pos_global)

                    # Realizar la suma
                    new_y = self.builder.add(current_y, move_amount)

                    # Almacenar el resultado en la variable global
                    self.builder.store(new_y, y_pos_global)

                    # Actualizar la variable de instancia
                    self.y_position += referenced_value

                    result = f"Movido {referenced_value} unidades hacia arriba. Nueva posicion en Y: {self.y_position}"
                    print(result)
                    return result
                else:
                    error_msg = f"Error Semantico: No se puede mover '{referenced_value}' unidades. Se esperaba un numero."
                    print(error_msg)
                    self.semantic_errors.append(error_msg)
                    return None
            else:
                error_msg = f"Error Semantico: La variable '{referenced_var_name}' no está definida."
                print(error_msg)
                self.semantic_errors.append(error_msg)
                return None
        else:
            # Evaluar el valor directamente
            move_units_value = self.visit(move_units)

            if isinstance(move_units_value, (int, float)):
                # Cargar el valor actual de y_position
                current_y = self.builder.load(y_pos_global)

                # Crear una constante LLVM con el valor de movimiento
                move_amount = ir.Constant(ir.IntType(32), int(move_units_value))

                # Realizar la suma
                new_y = self.builder.add(current_y, move_amount)

                # Almacenar el resultado en la variable global
                self.builder.store(new_y, y_pos_global)

                # Actualizar la variable de instancia
                self.y_position += move_units_value

                result = f"Movido {move_units_value} unidades hacia arriba. Nueva posicion en Y: {self.y_position}"
                print(result)
                return result
            else:
                error_msg = f"Error Semantico: No se puede mover '{move_units_value}' unidades. Se esperaba un numero."
                print(error_msg)
                self.semantic_errors.append(error_msg)
                return None

    def visit_continuedownstatement(self, node):
        move_units = node.move_units

        # Obtener la variable global y_position
        y_pos_global = self.global_vars["y_position"]
        y_pos_global.linkage = "common"
        y_pos_global.global_constant = False

        if not hasattr(y_pos_global, 'initializer') or y_pos_global.initializer is None:
            y_pos_global.initializer = ir.Constant(ir.IntType(32), 0)

        if isinstance(move_units.value, IdExpression):
            referenced_var_name = move_units.value.var_name
            if f"{referenced_var_name}_{self.variable_context.current_procedure}" in self.variable_context.variables or \
                    f"{referenced_var_name}_Main" in self.variable_context.variables:
                referenced_full_name = f"{referenced_var_name}_{self.variable_context.current_procedure}" \
                    if f"{referenced_var_name}_{self.variable_context.current_procedure}" in self.variable_context.variables \
                    else f"{referenced_var_name}_Main"

                referenced_value = self.variable_context.get_variable(referenced_full_name)

                if isinstance(referenced_value, bool):
                    error_msg = f"Error Semantico: No se puede mover '{referenced_value}' unidades. Se esperaba un numero."
                    print(error_msg)
                    self.semantic_errors.append(error_msg)
                    return None

                if isinstance(referenced_value, (int, float)):
                    # Si la variable referenciada está en la tabla de símbolos
                    if referenced_var_name in self.symbol_table:
                        move_value_ptr = self.symbol_table[referenced_var_name]
                        move_amount = self.builder.load(move_value_ptr)
                    else:
                        move_amount = ir.Constant(ir.IntType(32), int(referenced_value))

                    # Cargar el valor actual de y_position
                    current_y = self.builder.load(y_pos_global)

                    # Realizar la resta
                    neg_move = self.builder.sub(ir.Constant(ir.IntType(32), 0), move_amount)
                    new_y = self.builder.add(current_y, neg_move)

                    # Almacenar el resultado
                    self.builder.store(new_y, y_pos_global)

                    # Actualizar la variable de instancia
                    self.y_position -= referenced_value
                    result = f"Movido {referenced_value} unidades hacia abajo. Nueva posicion en Y: {self.y_position}"
                    print(result)
                    return result
                else:
                    error_msg = f"Error Semantico: No se puede mover '{referenced_value}' unidades. Se esperaba un numero."
                    print(error_msg)
                    self.semantic_errors.append(error_msg)
                    return None
            else:
                error_msg = f"Error Semantico: La variable '{referenced_var_name}' no está definida."
                print(error_msg)
                self.semantic_errors.append(error_msg)
                return None
        else:
            move_units_value = self.visit(move_units)

            if isinstance(move_units_value, (int, float)):
                # Cargar el valor actual de y_position
                current_y = self.builder.load(y_pos_global)

                # Crear una constante negativa para el movimiento hacia abajo
                neg_move = self.builder.sub(ir.Constant(ir.IntType(32), 0),
                                            ir.Constant(ir.IntType(32), int(move_units_value)))

                # Realizar la suma con el valor negativo (equivalente a resta)
                new_y = self.builder.add(current_y, neg_move)

                # Almacenar el resultado
                self.builder.store(new_y, y_pos_global)

                # Actualizar la variable de instancia
                self.y_position -= move_units_value

                result = f"Movido {move_units_value} unidades hacia abajo. Nueva posicion en Y: {self.y_position}"
                print(result)
                return result
            else:
                error_msg = f"Error Semantico: No se puede mover '{move_units_value}' unidades. Se esperaba un numero."
                print(error_msg)
                self.semantic_errors.append(error_msg)
                return None

    def visit_continuerightstatement(self, node):
        move_units = node.move_units

        # Obtener la variable global x_position
        x_pos_global = self.global_vars["x_position"]
        x_pos_global.linkage = "common"
        x_pos_global.global_constant = False

        if not hasattr(x_pos_global, 'initializer') or x_pos_global.initializer is None:
            x_pos_global.initializer = ir.Constant(ir.IntType(32), 0)

        if isinstance(move_units.value, IdExpression):
            referenced_var_name = move_units.value.var_name
            if f"{referenced_var_name}_{self.variable_context.current_procedure}" in self.variable_context.variables or \
                    f"{referenced_var_name}_Main" in self.variable_context.variables:
                referenced_full_name = f"{referenced_var_name}_{self.variable_context.current_procedure}" \
                    if f"{referenced_var_name}_{self.variable_context.current_procedure}" in self.variable_context.variables \
                    else f"{referenced_var_name}_Main"

                referenced_value = self.variable_context.get_variable(referenced_full_name)

                if isinstance(referenced_value, bool):
                    error_msg = f"Error Semantico: No se puede mover '{referenced_value}' unidades. Se esperaba un numero."
                    print(error_msg)
                    self.semantic_errors.append(error_msg)
                    return None

                if isinstance(referenced_value, (int, float)):
                    # Si la variable referenciada está en la tabla de símbolos
                    if referenced_var_name in self.symbol_table:
                        move_value_ptr = self.symbol_table[referenced_var_name]
                        move_amount = self.builder.load(move_value_ptr)
                    else:
                        move_amount = ir.Constant(ir.IntType(32), int(referenced_value))

                    # Cargar el valor actual de x_position
                    current_x = self.builder.load(x_pos_global)

                    # Realizar la suma
                    new_x = self.builder.add(current_x, move_amount)

                    # Almacenar el resultado
                    self.builder.store(new_x, x_pos_global)

                    # Actualizar la variable de instancia
                    self.x_position += referenced_value
                    result = f"Movido {referenced_value} unidades hacia la derecha. Nueva posicion en X: {self.x_position}"
                    print(result)
                    return result
                else:
                    error_msg = f"Error Semantico: No se puede mover '{referenced_value}' unidades. Se esperaba un numero."
                    print(error_msg)
                    self.semantic_errors.append(error_msg)
                    return None
            else:
                error_msg = f"Error Semantico: La variable '{referenced_var_name}' no está definida."
                print(error_msg)
                self.semantic_errors.append(error_msg)
                return None
        else:
            move_units_value = self.visit(move_units)

            if isinstance(move_units_value, (int, float)):
                # Cargar el valor actual de x_position
                current_x = self.builder.load(x_pos_global)

                # Crear constante para el movimiento
                move_amount = ir.Constant(ir.IntType(32), int(move_units_value))

                # Realizar la suma
                new_x = self.builder.add(current_x, move_amount)

                # Almacenar el resultado
                self.builder.store(new_x, x_pos_global)

                # Actualizar la variable de instancia
                self.x_position += move_units_value

                result = f"Movido {move_units_value} unidades hacia la derecha. Nueva posicion en X: {self.x_position}"
                print(result)
                return result
            else:
                error_msg = f"Error Semantico: No se puede mover '{move_units_value}' unidades. Se esperaba un numero."
                print(error_msg)
                self.semantic_errors.append(error_msg)
                return None

    def visit_continueleftstatement(self, node):
        move_units = node.move_units

        # Obtener la variable global x_position
        x_pos_global = self.global_vars["x_position"]
        x_pos_global.linkage = "common"
        x_pos_global.global_constant = False

        if not hasattr(x_pos_global, 'initializer') or x_pos_global.initializer is None:
            x_pos_global.initializer = ir.Constant(ir.IntType(32), 0)

        if isinstance(move_units.value, IdExpression):
            referenced_var_name = move_units.value.var_name
            if f"{referenced_var_name}_{self.variable_context.current_procedure}" in self.variable_context.variables or \
                    f"{referenced_var_name}_Main" in self.variable_context.variables:
                referenced_full_name = f"{referenced_var_name}_{self.variable_context.current_procedure}" \
                    if f"{referenced_var_name}_{self.variable_context.current_procedure}" in self.variable_context.variables \
                    else f"{referenced_var_name}_Main"

                referenced_value = self.variable_context.get_variable(referenced_full_name)

                if isinstance(referenced_value, bool):
                    error_msg = f"Error Semantico: No se puede mover '{referenced_value}' unidades. Se esperaba un numero."
                    print(error_msg)
                    self.semantic_errors.append(error_msg)
                    return None

                if isinstance(referenced_value, (int, float)):
                    # Si la variable referenciada está en la tabla de símbolos
                    if referenced_var_name in self.symbol_table:
                        move_value_ptr = self.symbol_table[referenced_var_name]
                        move_amount = self.builder.load(move_value_ptr)
                    else:
                        move_amount = ir.Constant(ir.IntType(32), int(referenced_value))

                    # Cargar el valor actual de x_position
                    current_x = self.builder.load(x_pos_global)

                    # Realizar la resta
                    neg_move = self.builder.sub(ir.Constant(ir.IntType(32), 0), move_amount)
                    new_x = self.builder.add(current_x, neg_move)

                    # Almacenar el resultado
                    self.builder.store(new_x, x_pos_global)

                    # Actualizar la variable de instancia
                    self.x_position -= referenced_value
                    result = f"Movido {referenced_value} unidades hacia la izquierda. Nueva posicion en X: {self.x_position}"
                    print(result)
                    return result
                else:
                    error_msg = f"Error Semantico: No se puede mover '{referenced_value}' unidades. Se esperaba un numero."
                    print(error_msg)
                    self.semantic_errors.append(error_msg)
                    return None
            else:
                error_msg = f"Error Semantico: La variable '{referenced_var_name}' no está definida."
                print(error_msg)
                self.semantic_errors.append(error_msg)
                return None
        else:
            move_units_value = self.visit(move_units)

            if isinstance(move_units_value, (int, float)):
                # Cargar el valor actual de x_position
                current_x = self.builder.load(x_pos_global)

                # Crear una constante negativa para el movimiento hacia la izquierda
                neg_move = self.builder.sub(ir.Constant(ir.IntType(32), 0),
                                            ir.Constant(ir.IntType(32), int(move_units_value)))

                # Realizar la suma con el valor negativo (equivalente a resta)
                new_x = self.builder.add(current_x, neg_move)

                # Almacenar el resultado
                self.builder.store(new_x, x_pos_global)

                # Actualizar la variable de instancia
                self.x_position -= move_units_value

                result = f"Movido {move_units_value} unidades hacia la izquierda. Nueva posicion en X: {self.x_position}"
                print(result)
                return result
            else:
                error_msg = f"Error Semantico: No se puede mover '{move_units_value}' unidades. Se esperaba un numero."
                print(error_msg)
                self.semantic_errors.append(error_msg)
                return None

    def visit_turnrightstatement(self, node):
        move_units = node.move_units

        if isinstance(move_units.value, IdExpression):
            referenced_var_name = move_units.value.var_name
            if f"{referenced_var_name}_{self.variable_context.current_procedure}" in self.variable_context.variables or \
                    f"{referenced_var_name}_Main" in self.variable_context.variables:
                referenced_full_name = f"{referenced_var_name}_{self.variable_context.current_procedure}" \
                    if f"{referenced_var_name}_{self.variable_context.current_procedure}" in self.variable_context.variables \
                    else f"{referenced_var_name}_Main"

                referenced_value = self.variable_context.get_variable(referenced_full_name)
                if isinstance(referenced_value, bool):
                    print(f"Error Semantico: No se puede mover '{referenced_value}' unidades. Se esperaba un numero.")
                    self.semantic_errors.append(
                        f"Error Semantico: No se puede mover '{referenced_value}' unidades. Se esperaba un numero.")
                    return None
                if isinstance(referenced_value, (int, float)):
                    self.angle = referenced_value
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
                self.angle = move_units_value
                result = f"Movido {move_units_value} unidades hacia la derecha. Nueva posicion en X: {self.x_position}"
                print(result)
                return result
            else:
                print(f"Error Semantico: No se puede mover '{move_units_value}' unidades. Se esperaba un numero.")
                self.semantic_errors.append(
                    f"Error Semantico: No se puede mover '{move_units_value}' unidades. Se esperaba un numero.")
                return None

    def visit_turnleftstatement(self, node):
        move_units = node.move_units

        if isinstance(move_units.value, IdExpression):
            referenced_var_name = move_units.value.var_name
            if f"{referenced_var_name}_{self.variable_context.current_procedure}" in self.variable_context.variables or \
                    f"{referenced_var_name}_Main" in self.variable_context.variables:
                referenced_full_name = f"{referenced_var_name}_{self.variable_context.current_procedure}" \
                    if f"{referenced_var_name}_{self.variable_context.current_procedure}" in self.variable_context.variables \
                    else f"{referenced_var_name}_Main"

                referenced_value = self.variable_context.get_variable(referenced_full_name)
                if isinstance(referenced_value, bool):
                    print(f"Error Semantico: No se puede mover '{referenced_value}' unidades. Se esperaba un numero.")
                    self.semantic_errors.append(
                        f"Error Semantico: No se puede mover '{referenced_value}' unidades. Se esperaba un numero.")
                    return None
                if isinstance(referenced_value, (int, float)):
                    self.angle -= referenced_value
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
                self.angle -= move_units_value
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
        x_val = self.visit(node.x_val)
        y_val = self.visit(node.y_val)

        # Obtener las variables globales
        x_pos_global = self.global_vars["x_position"]
        y_pos_global = self.global_vars["y_position"]

        # Asegurar que son modificables
        x_pos_global.linkage = "common"
        y_pos_global.linkage = "common"
        x_pos_global.global_constant = False
        y_pos_global.global_constant = False

        # Validar contexto y tipos
        if isinstance(x_val, bool):
            print(
                f"Error Semantico: La posicion X no puede ser un booleano. Se obtuvo '{x_val}' de tipo '{type(x_val).__name__}'.")
            self.semantic_errors.append(
                f"Error Semantico: La posicion X no puede ser un booleano. Se obtuvo '{x_val}' de tipo '{type(x_val).__name__}'.")
            return None

        if isinstance(y_val, bool):
            print(
                f"Error Semantico: La posicion Y no puede ser un booleano. Se obtuvo '{y_val}' de tipo '{type(y_val).__name__}'.")
            self.semantic_errors.append(
                f"Error Semantico: La posicion Y no puede ser un booleano. Se obtuvo '{y_val}' de tipo '{type(y_val).__name__}'.")
            return None

        # Crear constantes LLVM para los nuevos valores
        x_constant = ir.Constant(ir.IntType(32), int(x_val))
        y_constant = ir.Constant(ir.IntType(32), int(y_val))

        # Almacenar los nuevos valores
        self.builder.store(x_constant, x_pos_global)
        self.builder.store(y_constant, y_pos_global)

        # Actualizar las variables de instancia
        self.x_position = x_val
        self.y_position = y_val

        result = f"Posicion actualizada a X: {self.x_position}, Y: {self.y_position}"
        print(result)
        return result

    def visit_posxstatement(self, node):
        # Obtener el valor de X
        x_val = self.visit(node.x_val)

        # Obtener la variable global x_position
        x_pos_global = self.global_vars["x_position"]
        x_pos_global.linkage = "common"
        x_pos_global.global_constant = False

        # Verificación de tipo booleano
        if isinstance(x_val, bool):
            print(
                f"Error Semantico: La posicion X no puede ser un booleano. Se obtuvo '{x_val}' de tipo '{type(x_val).__name__}'.")
            self.semantic_errors.append(
                f"Error Semantico: La posicion X no puede ser un booleano. Se obtuvo '{x_val}' de tipo '{type(x_val).__name__}'.")
            return None

        # Crear constante LLVM para el nuevo valor
        x_constant = ir.Constant(ir.IntType(32), int(x_val))

        # Almacenar el nuevo valor
        self.builder.store(x_constant, x_pos_global)

        # Actualizar la variable de instancia
        self.x_position = x_val

        result = f"Posicion actualizada a X: {self.x_position}, Y: {self.y_position}"
        print(result)
        return result

    def visit_posystatement(self, node):
        # Obtener el valor de Y
        y_val = self.visit(node.y_val)

        # Obtener la variable global y_position
        y_pos_global = self.global_vars["y_position"]
        y_pos_global.linkage = "common"
        y_pos_global.global_constant = False

        # Verificación de tipo booleano
        if isinstance(y_val, bool):
            print(
                f"Error Semantico: La posicion Y no puede ser un booleano. Se obtuvo '{y_val}' de tipo '{type(y_val).__name__}'.")
            self.semantic_errors.append(
                f"Error Semantico: La posicion Y no puede ser un booleano. Se obtuvo '{y_val}' de tipo '{type(y_val).__name__}'.")
            return None

        # Crear constante LLVM para el nuevo valor
        y_constant = ir.Constant(ir.IntType(32), int(y_val))

        # Almacenar el nuevo valor
        self.builder.store(y_constant, y_pos_global)

        # Actualizar la variable de instancia
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
        # Obtener la variable global pen_down
        pen_down_global = self.global_vars["pen_down"]
        pen_down_global.linkage = "common"
        pen_down_global.global_constant = False

        # Crear constante LLVM para True (1)
        true_constant = ir.Constant(ir.IntType(1), 1)

        # Almacenar True en la variable global
        self.builder.store(true_constant, pen_down_global)

        # Actualizar la variable de instancia
        self.pen_down = True
        result = "Lapicero colocado en la superficie (Down)"
        print(result)
        return result

    def visit_upstatement(self, node):
        # Obtener la variable global pen_down
        pen_down_global = self.global_vars["pen_down"]
        pen_down_global.linkage = "common"
        pen_down_global.global_constant = False

        # Crear constante LLVM para False (0)
        false_constant = ir.Constant(ir.IntType(1), 0)

        # Almacenar False en la variable global
        self.builder.store(false_constant, pen_down_global)

        # Actualizar la variable de instancia
        self.pen_down = False
        result = "Lapicero levantado de la superficie (Up)"
        print(result)
        return result

    def visit_beginningstatement(self, node):
        # Obtener las variables globales
        x_pos_global = self.global_vars["x_position"]
        y_pos_global = self.global_vars["y_position"]

        # Asegurar que las variables son modificables
        x_pos_global.linkage = "common"
        y_pos_global.linkage = "common"
        x_pos_global.global_constant = False
        y_pos_global.global_constant = False

        # Crear constantes LLVM para la posición (1,1)
        one = ir.Constant(ir.IntType(32), 1)

        # Almacenar los nuevos valores (1,1) en las variables globales
        self.builder.store(one, x_pos_global)
        self.builder.store(one, y_pos_global)

        # Actualizar las variables de instancia
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

        # Generar IR LLVM para la comparación
        if isinstance(left, bool):  # Comparación entre booleanos
            left_value = ir.Constant(ir.IntType(1), int(left))  # Convertir booleano a i1
            right_value = ir.Constant(ir.IntType(1), int(right))  # Convertir booleano a i1
            result = self.builder.icmp_unsigned("==", left_value, right_value)
        elif isinstance(left, int):  # Comparación entre enteros
            left_value = ir.Constant(ir.IntType(32), left)
            right_value = ir.Constant(ir.IntType(32), right)
            result = self.builder.icmp_signed("==", left_value, right_value)
        else:
            error_msg = f"Error Semántico: Operación '==' no soportada para el tipo {type(left).__name__}."
            print(error_msg)
            self.semantic_errors.append(error_msg)
            return None
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
        # Generar IR LLVM para la operación AND
        if isinstance(left, bool) and isinstance(right, bool):  # Operación entre booleanos
            left_value = ir.Constant(ir.IntType(1), int(left))  # Convertir a i1
            right_value = ir.Constant(ir.IntType(1), int(right))  # Convertir a i1
            llvm_result = self.builder.and_(left_value, right_value)
        elif isinstance(left, int) and isinstance(right, int):  # Operación entre enteros
            left_value = ir.Constant(ir.IntType(32), left)  # Convertir a i32
            right_value = ir.Constant(ir.IntType(32), right)  # Convertir a i32
            left_bool = self.builder.trunc(left_value, ir.IntType(1))  # Reducir a i1
            right_bool = self.builder.trunc(right_value, ir.IntType(1))  # Reducir a i1
            llvm_result = self.builder.and_(left_bool, right_bool)  # Operación AND en i1
        else:
            error_msg = f"Error Semántico: Operación 'AND' no soportada para los tipos {type(left).__name__} y {type(right).__name__}."
            print(error_msg)
            self.semantic_errors.append(error_msg)
            return None
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
        # Generar IR LLVM para la operación OR
        if isinstance(left, bool) and isinstance(right, bool):  # Operación entre booleanos
            left_value = ir.Constant(ir.IntType(1), int(left))  # Convertir a i1
            right_value = ir.Constant(ir.IntType(1), int(right))  # Convertir a i1
            llvm_result = self.builder.or_(left_value, right_value)
        elif isinstance(left, int) and isinstance(right, int):  # Operación entre enteros
            left_value = ir.Constant(ir.IntType(32), left)  # Convertir a i32
            right_value = ir.Constant(ir.IntType(32), right)  # Convertir a i32
            left_bool = self.builder.trunc(left_value, ir.IntType(1))  # Reducir a i1
            right_bool = self.builder.trunc(right_value, ir.IntType(1))  # Reducir a i1
            llvm_result = self.builder.or_(left_bool, right_bool)  # Operación OR en i1
        else:
            error_msg = f"Error Semántico: Operación 'OR' no soportada para los tipos {type(left).__name__} y {type(right).__name__}."
            print(error_msg)
            self.semantic_errors.append(error_msg)
            return None
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
        # Generar IR LLVM para la comparación
        if isinstance(left, int) and isinstance(right, int):  # Comparación entre enteros
            left_value = ir.Constant(ir.IntType(32), left)  # Convertir a i32
            right_value = ir.Constant(ir.IntType(32), right)  # Convertir a i32
            llvm_result = self.builder.icmp_signed(">", left_value, right_value)
        else:
            error_msg = f"Error Semántico: Operación '>' no soportada para los tipos {type(left).__name__} y {type(right).__name__}."
            print(error_msg)
            self.semantic_errors.append(error_msg)
            return None
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
        if isinstance(left, int) and isinstance(right, int):  # Comparación entre enteros
            left_value = ir.Constant(ir.IntType(32), left)  # Convertir a i32
            right_value = ir.Constant(ir.IntType(32), right)  # Convertir a i32
            llvm_result = self.builder.icmp_signed("<", left_value, right_value)
        else:
            error_msg = f"Error Semántico: Operación '<' no soportada para los tipos {type(left).__name__} y {type(right).__name__}."
            print(error_msg)
            self.semantic_errors.append(error_msg)
            return None
        return result

    def visit_substrstatement(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)

        # Verificación de contexto para left
        if isinstance(node.left.value, IdExpression):
            referenced_var_name = node.left.value.var_name
            if referenced_var_name in self.symbol_table:
                left_value_ptr = self.symbol_table[referenced_var_name]
                left_value = self.builder.load(left_value_ptr)
            else:
                left_value = ir.Constant(ir.IntType(32), int(left))
        else:
            left_value = ir.Constant(ir.IntType(32), int(left))

        # Verificación de contexto para right
        if isinstance(node.right.value, IdExpression):
            referenced_var_name = node.right.value.var_name
            if referenced_var_name in self.symbol_table:
                right_value_ptr = self.symbol_table[referenced_var_name]
                right_value = self.builder.load(right_value_ptr)
            else:
                right_value = ir.Constant(ir.IntType(32), int(right))
        else:
            right_value = ir.Constant(ir.IntType(32), int(right))

        # Verificar que los valores no sean booleanos
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

        # Verificar que N1 sea mayor o igual que N2
        if left < right:
            print(f"Error Semantico: N1 debe ser mayor o igual a N2.")
            self.semantic_errors.append(f"Error Semantico: N1 debe ser mayor o igual a N2.")
            return None

        # Realizar la resta en LLVM IR
        result = self.builder.sub(left_value, right_value)

        # Actualizar el resultado en Python
        python_result = left - right
        print(f"Sustraccion: {left} - {right} = {python_result}")
        return python_result

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
            if referenced_var_name in self.symbol_table:
                left_value_ptr = self.symbol_table[referenced_var_name]
                left_value = self.builder.load(left_value_ptr)
            else:
                left_value = ir.Constant(ir.IntType(32), int(left))
        else:
            left_value = ir.Constant(ir.IntType(32), int(left))

        # Verificación de contexto para right
        if isinstance(node.right.value, IdExpression):
            referenced_var_name = node.right.value.var_name
            if referenced_var_name in self.symbol_table:
                right_value_ptr = self.symbol_table[referenced_var_name]
                right_value = self.builder.load(right_value_ptr)
            else:
                right_value = ir.Constant(ir.IntType(32), int(right))
        else:
            right_value = ir.Constant(ir.IntType(32), int(right))

        # Verificar que los valores no sean booleanos
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

        # Realizar la multiplicación en LLVM IR
        result = self.builder.mul(left_value, right_value)

        # Actualizar el resultado en Python
        python_result = left * right
        print(f"Multiplicacion: {left} * {right} = {python_result}")
        return python_result

    def visit_divstatement(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)

        # Verificación de contexto para left
        if isinstance(node.left.value, IdExpression):
            referenced_var_name = node.left.value.var_name
            if referenced_var_name in self.symbol_table:
                left_value_ptr = self.symbol_table[referenced_var_name]
                left_value = self.builder.load(left_value_ptr)
            else:
                left_value = ir.Constant(ir.IntType(32), int(left))
        else:
            left_value = ir.Constant(ir.IntType(32), int(left))

        # Verificación de contexto para right
        if isinstance(node.right.value, IdExpression):
            referenced_var_name = node.right.value.var_name
            if referenced_var_name in self.symbol_table:
                right_value_ptr = self.symbol_table[referenced_var_name]
                right_value = self.builder.load(right_value_ptr)
            else:
                right_value = ir.Constant(ir.IntType(32), int(right))
        else:
            right_value = ir.Constant(ir.IntType(32), int(right))

        # Verificar que los valores no sean booleanos
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

        # Verificar división por cero
        if right == 0:
            print(f"Error Semantico: Division por cero.")
            self.semantic_errors.append(f"Error Semantico: Division por cero.")
            return None

        # Realizar la división entera en LLVM IR
        result = self.builder.sdiv(left_value, right_value)

        # Actualizar el resultado en Python
        python_result = left // right
        print(f"Division: {left} // {right} = {python_result}")
        return python_result

    def visit_sumstatement(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)

        # Verificación de contexto para left
        if isinstance(node.left.value, IdExpression):
            referenced_var_name = node.left.value.var_name
            if referenced_var_name in self.symbol_table:
                left_value_ptr = self.symbol_table[referenced_var_name]
                left_value = self.builder.load(left_value_ptr)
            else:
                left_value = ir.Constant(ir.IntType(32), int(left))
        else:
            left_value = ir.Constant(ir.IntType(32), int(left))

        # Verificación de contexto para right
        if isinstance(node.right.value, IdExpression):
            referenced_var_name = node.right.value.var_name
            if referenced_var_name in self.symbol_table:
                right_value_ptr = self.symbol_table[referenced_var_name]
                right_value = self.builder.load(right_value_ptr)
            else:
                right_value = ir.Constant(ir.IntType(32), int(right))
        else:
            right_value = ir.Constant(ir.IntType(32), int(right))

        # Verificar que los valores no sean booleanos
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

        # Realizar la suma en LLVM IR
        result = self.builder.add(left_value, right_value)

        # Actualizar el resultado en Python
        python_result = left + right
        print(f"Suma: {left} + {right} = {python_result}")
        return python_result

    def visit_forstatement(self, node):
        # Obtener valores de min_value y max_value
        min_value = self.visit(node.min_value)
        max_value = self.visit(node.max_value)

        # Verificaciones iniciales
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

        if min_value >= max_value:
            error_msg = "Error Semántico: max_value debe ser mayor que min_value."
            print(error_msg)
            self.semantic_errors.append(error_msg)
            return None

        # Validar el nombre de la variable
        if not re.match(r'^[a-z][a-zA-Z0-9*@]{2,9}$', node.variable):
            error_msg = f"Error Semántico: El nombre de la variable '{node.variable}' no cumple con las reglas."
            print(error_msg)
            self.semantic_errors.append(error_msg)
            return None

        # Crear la variable del bucle en el IR
        loop_var = self.builder.alloca(ir.IntType(32), name=node.variable)
        self.builder.store(ir.Constant(ir.IntType(32), min_value), loop_var)

        # Crear bloques básicos para el bucle
        loop_head = self.builder.append_basic_block(name="loop_head")
        loop_body = self.builder.append_basic_block(name="loop_body")
        loop_end = self.builder.append_basic_block(name="loop_end")

        # Saltar al encabezado del bucle
        self.builder.branch(loop_head)
        self.builder.position_at_end(loop_head)

        # Comparar si loop_var < max_value
        current_value = self.builder.load(loop_var)
        max_value_ir = ir.Constant(ir.IntType(32), max_value)
        condition = self.builder.icmp_signed("<", current_value, max_value_ir)
        self.builder.cbranch(condition, loop_body, loop_end)

        # Generar cuerpo del bucle en LLVM
        self.builder.position_at_end(loop_body)

        # Visitar y generar las instrucciones para el cuerpo del bucle
        for statement in node.body:
            self.visit(statement)

        # Incrementar la variable del bucle
        incremented_value = self.builder.add(current_value, ir.Constant(ir.IntType(32), 1))
        self.builder.store(incremented_value, loop_var)

        # Saltar de nuevo al encabezado del bucle
        self.builder.branch(loop_head)

        # Finalizar el bucle
        self.builder.position_at_end(loop_end)

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
            error_msg = f"Error Semantico: La variable '{referenced_var_name}' no está definida."
            print(error_msg)
            self.semantic_errors.append(error_msg)
            return None

        # Obtener el valor y tipo de la variable
        variable_value = self.variable_context.get_variable(referenced_full_name)
        variable_type = self.variable_context.get_variable_type(referenced_full_name)
        print(f"Valor de la variable: {variable_value}")

        # Obtener el alloca de la variable desde la tabla de símbolos
        if referenced_var_name in self.symbol_table:
            variable_ptr = self.symbol_table[referenced_var_name]
        else:
            error_msg = f"Error Semantico: No se encontró la variable '{referenced_var_name}' en la tabla de símbolos."
            print(error_msg)
            self.semantic_errors.append(error_msg)
            return None

        # Cargar el valor de la variable en LLVM IR
        variable_value_llvm = self.builder.load(variable_ptr, name=f"{referenced_var_name}_value")

        # Convertir el valor a i32 si es necesario
        if variable_type == "BOOLEAN":
            # Extender el valor de i1 a i32
            variable_value_llvm = self.builder.zext(variable_value_llvm, ir.IntType(32),
                                                    name=f"{referenced_var_name}_i32")
        elif variable_type == "NUMBER":
            # Ya es de tipo i32
            pass
        else:
            error_msg = f"Error Semántico: Tipo de dato no soportado para la variable '{node.variable}'."
            print(error_msg)
            self.semantic_errors.append(error_msg)
            return None

        # Crear el bloque de salida del switch
        end_switch_block = self.builder.append_basic_block(name="end_switch")

        # Crear el switch instruction
        switch_inst = self.builder.switch(variable_value_llvm, end_switch_block)

        # Diccionario para almacenar los bloques de cada caso
        case_blocks = {}

        # Generar los bloques para cada cláusula When
        for when_clause in node.when_clauses:
            condition_value = self.visit(when_clause.condition)
            print(f"Evaluando condición: {condition_value}")

            # Verificar el tipo de la condición
            if isinstance(condition_value, bool):
                condition_value = int(condition_value)
            elif isinstance(condition_value, int):
                pass
            else:
                error_msg = f"Error Semántico: Tipo de dato no soportado en la condición del Case: '{type(condition_value).__name__}'."
                print(error_msg)
                self.semantic_errors.append(error_msg)
                return None

            # Crear un bloque para este caso
            case_block = self.builder.append_basic_block(name=f"case_{condition_value}")
            case_blocks[condition_value] = case_block

            # Agregar el caso al switch
            condition_llvm_value = ir.Constant(ir.IntType(32), condition_value)
            switch_inst.add_case(condition_llvm_value, case_block)

        # Si hay cláusula Else, crear su bloque
        if node.else_clause:
            else_block = self.builder.append_basic_block(name="case_else")
            switch_inst.default = else_block
        else:
            switch_inst.default = end_switch_block

        # Generar código para cada caso
        for when_clause in node.when_clauses:
            condition_value = self.visit(when_clause.condition)
            case_block = case_blocks[condition_value]
            self.builder.position_at_end(case_block)

            # Generar código para el cuerpo del When
            for statement in when_clause.body:
                self.visit(statement)

            # Al final del caso, saltar al bloque de fin del switch
            self.builder.branch(end_switch_block)

        # Generar código para la cláusula Else si existe
        if node.else_clause:
            self.builder.position_at_end(else_block)
            print("Ninguna condición cumplida, ejecutando cláusula Else")
            for statement in node.else_clause:
                self.visit(statement)
            self.builder.branch(end_switch_block)

        # Posicionar el builder en el bloque end_switch_block para continuar
        self.builder.position_at_end(end_switch_block)

        return None

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
                if condition_result:  # Verificar si la lista no está vacía
                    condition_result = condition_result[0]
                else:
                    print("La condición resultó en una lista vacía. Saliendo del bucle While.")
                    break

            if condition_result is None:
                print("Saliendo del bucle While")
                break  # Salir del bucle si el resultado de la condición es None

            if not condition_result:
                print("Saliendo del bucle While")
                break

            # Ejecutar el cuerpo
            for statement in node.body:
                self.visit(statement)

    def visit_procedurestatement(self, node):

        # Crear la función LLVM para este procedimiento
        func_type = ir.FunctionType(ir.VoidType(), [])  # Sin parámetros y sin retorno
        func = ir.Function(self.module, func_type, name=node.procedure_name)

        # Crear un bloque de entrada para el procedimiento
        block = func.append_basic_block(name="entry")
        self.builder = ir.IRBuilder(block)

        print(f"Registrando procedimiento: {node.procedure_name}")

        # Extraer los nombres de los parámetros
        parameters = []
        for param in node.arguments:
            if isinstance(param, IdExpression):
                parameters.append(param.var_name)
            else:
                parameters.append(str(param))

        param_count = len(parameters)

        # Verificar si ya existe un procedimiento con el mismo nombre y cantidad de parámetros
        if self.proc_var_tracker.get_procedure(node.procedure_name, param_count):
            error_msg = (f"Error Semántico: El procedimiento '{node.procedure_name}' ya está definido "
                         f"con {param_count} parámetros.")
            print(error_msg)
            self.semantic_errors.append(error_msg)
            return None  # Salir si ya existe un procedimiento con el mismo nombre y número de parámetros

        # Registrar el procedimiento en el tracker
        self.proc_var_tracker.register_procedure(node.procedure_name, parameters)

        print(f"Procedimiento {node.procedure_name} registrado con {param_count} parámetros: {parameters}")
        if node.procedure_name == "Main":
            print("Ejecutando el procedimiento 'Main'...")
            self.visit_callstatement(node)
        self.builder.ret_void()
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
            if isinstance(stmt, ProcedureStatement) and stmt.procedure_name == procedure_name and len(
                    stmt.arguments) == param_count:
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

    def check_main(self):
        # Inicializamos las variables de conteo
        main_count = 0
        main_parameters = None

        # Iterar sobre todas las claves (procedimientos) en el tracker
        for proc_key in self.proc_var_tracker.procedures:
            if proc_key[0] == "Main":  # Verificamos si el nombre del procedimiento es "Main"
                main_count += 1
                main_parameters = self.proc_var_tracker.procedures[proc_key]["params"]

        # Verificar si no se encontró el procedimiento Main
        if main_count == 0:
            print("Error Semántico: No se ha registrado el procedimiento 'Main'.")
            self.semantic_errors.append("Error Semántico: No se ha registrado el procedimiento 'Main'.")

        # Verificar si hay más de un Main
        elif main_count > 1:
            print("Error Semántico: Hay más de un procedimiento 'Main' registrado.")
            self.semantic_errors.append("Error Semántico: Hay más de un procedimiento 'Main' registrado.")

        # Verificar si Main tiene parámetros
        elif main_parameters and len(main_parameters) > 0:
            print("Error Semántico: El procedimiento 'Main' no debe tener parámetros.")
            self.semantic_errors.append("Error Semántico: El procedimiento 'Main' no debe tener parámetros.")

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
        self.check_main()

    def print_procedure_tracker(self):
        self.proc_var_tracker.print_summary()

    def validate_ir(self):
        try:
            llvm_ir = str(self.module)
            llvm_module = binding.parse_assembly(llvm_ir)
            llvm_module.verify()
            print("El IR es válido.")
            print(self.module)
        except Exception as e:
            print(f"Error de validación: {e}")