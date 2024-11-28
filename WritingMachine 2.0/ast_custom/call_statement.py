from ast_custom.node import ASTNode

class CallStatement(ASTNode):
    def __init__(self, procedure_name, arguments):
        self.procedure_name = procedure_name
        self.arguments = arguments if arguments is not None else []

    def accept(self, visitor):
        return visitor.visit_callstatement(self)

    def __repr__(self):
        return f"CallStatement(procedure_name={self.procedure_name}, arguments={self.arguments})"
