from writingMachine.ast.node import ASTNode


class DownStatement(ASTNode):
    def accept(self, visitor):
        return visitor.visit_downstatement(self)
