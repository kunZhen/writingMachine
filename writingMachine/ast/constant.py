from .ast_node import ASTNode

class Constant(ASTNode):
    def __init__(self, value):
        self.value = value

    def execute(self, symbolTable):
        return self.value
