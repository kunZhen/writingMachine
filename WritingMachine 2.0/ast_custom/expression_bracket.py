from ast_custom.node import ASTNode


class ExpressionBracket(ASTNode):
    def __init__(self, expressions):
        self.expressions = expressions

    def accept(self, visitor):
        return visitor.visit_expressionbracket(self)
