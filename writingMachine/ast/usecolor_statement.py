from writingMachine.ast.node import ASTNode


class UseColorStatement(ASTNode):
    def __init__(self, color_value):
        self.color_value = color_value

    def accept(self, visitor):
        return visitor.visit_usecolorstatement(self)
