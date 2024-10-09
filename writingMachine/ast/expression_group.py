from writingMachine.ast.node import ASTNode


class ExpressionGroup(ASTNode):
    def __init__(self, expressions):
        self.expressions = expressions

    def accept(self, visitor):
        return visitor.visit_expressiongroup(self)
