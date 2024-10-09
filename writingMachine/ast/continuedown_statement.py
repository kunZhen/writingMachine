from writingMachine.ast.node import ASTNode


class ContinueDownStatement(ASTNode):
    def __init__(self, move_units):
        self.move_units = move_units

    def accept(self, visitor):
        return visitor.visit_continuedownstatement(self)

