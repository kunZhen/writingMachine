from .node import ASTNode

class Program(ASTNode):
    def __init__(self, statements):
        self.statements = statements  # Lista de nodos (statements)

    def accept(self, visitor):
        return visitor.visit_program(self)
