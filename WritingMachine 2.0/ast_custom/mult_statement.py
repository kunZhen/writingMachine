from ast_custom.node import ASTNode

class MultStatement(ASTNode):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def accept(self, visitor):
        return visitor.visit_multstatement(self)
