import random

from writingMachine.ast.boolean_expression import BooleanExpression
from writingMachine.ast.def_statement import DefStatement
from writingMachine.ast.id_expression import IdExpression
from writingMachine.ast.number_expression import NumberExpression
from writingMachine.ast.variable_context import VariableContext


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
        if isinstance(node.value, (NumberExpression, BooleanExpression, IdExpression)):
            return self.visit(node.value)
        return node.value
    def visit_for_statement(self, node):
        """Método para visitar un nodo ForStatement."""
        results = []
        if node.max_val <= node.min_val:
            print(f"Error: El valor máximo ({node.max_val}) debe ser mayor que el valor mínimo ({node.min_val}).")
            return results

        for i in range(node.min_val, node.max_val + 1):
            self.variable_context.set_variable(node.var_name, i)  # Usa el contexto de variables
            # Ejecutar el cuerpo del bucle
            result = self.visit(node.body)  # Llama al método visit para el cuerpo
            results.append(result)

        self.variable_context.remove_variable(node.var_name)  # Elimina la variable de control después del bucle
        print(f"For {node.var_name} from {node.min_val} to {node.max_val}: {results}")
        return results

    def visit_execute_statement(self, node):
        """Método para visitar un nodo ExecuteStatement."""
        return str(node.statement)  # Simplemente convierte el statement a string

    def visit_defstatement(self, node):
        value = self.visit(node.value)
        self.variable_context.set_variable(node.var_name, value)
        print(f"Definido {node.var_name} = {value}")
        return value

    def visit_putstatement(self, node):
        """Método para visitar un nodo PutStatement."""
        if node.var_name in self.variable_context.variables:
            self.variable_context.set_variable(node.var_name, self.visit(node.value))
            print(f"Actualizado {node.var_name} = {self.visit(node.value)}")
        else:
            print(f"Error: Variable '{node.var_name}' no definida")

    def visit_addstatement(self, node):
        if node.var_name not in self.variable_context.variables:
            print(f"Error: '{node.var_name}' no es una variable válida.")
            return

        current_value = self.variable_context.get_variable(node.var_name)

        if node.increment_value is None:
            new_value = current_value + 1
        else:
            increment = self.visit(node.increment_value)
            if not isinstance(increment, (int, float)):
                print(f"Error: El incremento debe ser un número.")
                return
            new_value = current_value + increment

        self.variable_context.set_variable(node.var_name, new_value)
        print(f"Incrementado {node.var_name} de {current_value} a {new_value}")

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
        # Obtener los valores de N1 y N2
        left = node.left.accept(self)  # N1
        right = node.right.accept(self)  # N2

        # Verificar si N1 es mayor o igual a N2
        if left < right:
            raise ValueError("Error: N1 debe ser mayor o igual a N2.")

        # Realizar la sustracción
        result = left - right
        print(result)
        return result  # Retorna el resultado de la sustracción

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
        # Obtener los valores de N1 y N2
        left = node.left.accept(self)  # N1
        right = node.right.accept(self)  # N2

        # Realizar la multiplicación
        result = left * right
        print(result)
        return result  # Retorna el resultado de la multiplicación

    def visit_divstatement(self, node):
        # Obtener los valores de N1 y N2
        left = node.left.accept(self)  # N1
        right = node.right.accept(self)  # N2

        # Verificar que N2 no sea cero
        if right == 0:
            raise ValueError("Error: División por cero no permitida.")

        # Realizar la división entera (truncada)
        result = left // right
        print(result)
        return result  # Retorna el resultado de la división

    def visit_sumstatement(self, node):
        # Obtener los valores de N1 y N2
        left = node.left.accept(self)  # N1
        right = node.right.accept(self)  # N2

        # Realizar la suma
        result = left + right
        print(result)
        return result  # Retorna el resultado de la suma

    def visit_binaryoperation(self, node):
        left = node.left.accept(self)
        right = node.right.accept(self)
        if node.operator == '+':
            return left + right
        elif node.operator == '-':
            return left - right
        elif node.operator == '*':
            return left * right
        elif node.operator == '/':
            if right == 0:
                raise ValueError("División por cero")
            return left / right
        elif node.operator == '<':
            return left < right
        elif node.operator == '>':
            return left > right
        elif node.operator == '=':
            return left == right


    def visit_expressiongroup(self, node):
        # Aquí asumimos que node.expressions es una instancia de ExpressionList
        results = node.expressions.accept(self)  # Llama al visit para la lista de expresiones
        return results

    def visit_expressionbracket(self, node):
        # Visitar todas las expresiones en el corchete
        results = [expr.accept(self) for expr in node.expressions]
        return results  # Retorna los resultados de todas las expresiones

    def visit_expressionlist(self, node):
        # Aquí iteramos sobre las expresiones dentro del nodo ExpressionList
        results = [expr.accept(self) for expr in node.expressions]
        return results  # Retorna los resultados de todas las expresiones
    def visit_idexpression(self, node):
        return self.variable_context.get_variable(node.var_name)
    def visit_numberexpression(self, node):
        return node.value

    def visit_booleanexpression(self, node):
        return node.value