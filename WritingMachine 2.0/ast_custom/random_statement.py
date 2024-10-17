from ast_custom.node import ASTNode

class RandomStatement(ASTNode):
    def __init__(self, value):
        self.value = value

    def accept(self, visitor):
        return visitor.visit_randomstatement(self)
