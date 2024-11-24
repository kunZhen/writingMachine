from .node import Statement, ASTNode


class Expression(ASTNode):
    def __init__(self, value):
        self.value = value  # Valor de la expresión

    def accept(self, visitor):
        return visitor.visit_expression(self)
