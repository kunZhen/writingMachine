from .node import Expression  # Asegúrate de importar la clase base correcta

class BooleanExpression(Expression):
    def __init__(self, value):
        self.value = value  # El valor booleano

    def accept(self, visitor):
        return visitor.visit_booleanexpression(self)
