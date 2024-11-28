from ast_custom.node import ASTNode

class PosYStatement(ASTNode):
    def __init__(self, y_val):
        self.y_val = y_val

    def accept(self, visitor):
        return visitor.visit_posystatement(self)
