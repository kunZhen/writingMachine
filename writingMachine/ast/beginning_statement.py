from writingMachine.ast.node import ASTNode


class BeginningStatement(ASTNode):
    def accept(self, visitor):
        return visitor.visit_beginningstatement(self)
