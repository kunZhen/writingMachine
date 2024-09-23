from writingMachine.ast.node import Statement, ASTNode


class AddStatement(ASTNode):
    def __init__(self, var_name, increment_value=None):
        self.var_name = var_name
        self.increment_value = increment_value

    def accept(self, visitor):
        return visitor.visit_addstatement(self)
