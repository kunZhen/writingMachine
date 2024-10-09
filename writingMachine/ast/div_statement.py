from writingMachine.ast.node import ASTNode


class DivStatement(ASTNode):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def accept(self, visitor):
        return visitor.visit_divstatement(self)
