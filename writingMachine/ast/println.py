from .ast_node import ASTNode

class Println(ASTNode):
    def __init__(self, expression: ASTNode):
        self.expression = expression

    def execute(self, symbolTable):
        print(self.expression.execute(symbolTable))
