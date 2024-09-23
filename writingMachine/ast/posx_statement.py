from writingMachine.ast.node import ASTNode


class PosXStatement(ASTNode):
    def __init__(self, x_val):
        self.x_val = x_val

    def accept(self, visitor):
        return visitor.visit_posxstatement(self)
