from .node import Statement

class ExecuteStatement(Statement):
    def __init__(self, statement):
        self.statement = statement  # El statement que se va a ejecutar

    def accept(self, visitor):
        return visitor.visit_execute_statement(self)
