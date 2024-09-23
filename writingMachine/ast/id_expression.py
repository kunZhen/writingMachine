from .node import Expression  # Asegúrate de importar la clase base correcta

class IdExpression(Expression):
    def __init__(self, var_name):
        self.var_name = var_name  # Nombre de la variable

    def accept(self, visitor):
        return visitor.visit_idexpression(self)
