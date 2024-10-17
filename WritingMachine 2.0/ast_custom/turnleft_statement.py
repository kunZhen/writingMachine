from ast_custom.node import ASTNode

class TurnLeftStatement(ASTNode):
    def __init__(self, move_units):
        self.move_units = move_units

    def accept(self, visitor):
        return visitor.visit_turnleftstatement(self)