from ast_custom.node import ASTNode


class DefStatement(ASTNode):
    def __init__(self, var_name, value):
        self.var_name = var_name
        self.value = value

    def accept(self, visitor):
        return visitor.visit_defstatement(self)
