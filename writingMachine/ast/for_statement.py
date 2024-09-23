from .node import Statement

class ForStatement(Statement):
    def __init__(self, var_name, min_val, max_val, body):
        self.var_name = var_name  # Nombre de la variable de control
        self.min_val = min_val  # Valor mínimo
        self.max_val = max_val  # Valor máximo
        self.body = body  # Cuerpo del bucle

    def accept(self, visitor):
        return visitor.visit_for_statement(self)
