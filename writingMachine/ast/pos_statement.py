from writingMachine.ast.node import ASTNode


class PosStatement(ASTNode):
    def __init__(self, x_val, y_val):
        self.x_val = x_val
        self.y_val = y_val

    def accept(self, visitor):
        return visitor.visit_posstatement(self)