from ast_custom.node import ASTNode

class UpStatement(ASTNode):
    def accept(self, visitor):
        return visitor.visit_upstatement(self)
