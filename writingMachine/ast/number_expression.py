from .node import Expression  # Asegúrate de importar la clase base correcta

class NumberExpression(Expression):
    def __init__(self, value):
        self.value = value  # El valor del número

    def accept(self, visitor):
        return visitor.visit_numberexpression(self)
