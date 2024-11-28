from .node import Statement

class PutStatement(Statement):
    def __init__(self, var_name, value):
        self.var_name = var_name
        self.value = value

    def accept(self, visitor):
        return visitor.visit_putstatement(self)
