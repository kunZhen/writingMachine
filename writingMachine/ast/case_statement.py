from writingMachine.ast.node import ASTNode


class CaseStatement(ASTNode):
    def __init__(self, variable, when_clauses, else_clause):
        self.variable = variable
        self.when_clauses = when_clauses
        self.else_clause = else_clause if isinstance(else_clause, list) else [else_clause]
    def __repr__(self):
        return f"CaseStatement(variable={self.variable}, when_clauses={self.when_clauses}, else_clause={self.else_clause})"
