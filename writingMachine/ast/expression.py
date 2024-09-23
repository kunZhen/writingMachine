from .node import Statement

class Expression(Statement):
    def __init__(self, value):
        self.value = value  # Valor de la expresión

    def accept(self, visitor):
        return visitor.visit_expression(self)
