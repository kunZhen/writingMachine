from .ast_node import ASTNode

class VarAssign(ASTNode):
    def __init__(self, name: str, expression: ASTNode):
        self.name = name
        self.expression = expression

    def execute(self, symbolTable):
        symbolTable[self.name] = self.expression.execute(symbolTable)
