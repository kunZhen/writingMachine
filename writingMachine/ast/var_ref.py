from .ast_node import ASTNode

class VarRef(ASTNode):
    def __init__(self, name: str):
        self.name = name

    def execute(self, symbolTable):
        return symbolTable.get(self.name, None)
