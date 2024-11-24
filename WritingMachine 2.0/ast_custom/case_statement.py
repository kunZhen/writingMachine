from ast_custom.node import ASTNode


class CaseStatement(ASTNode):
    def __init__(self, variable, when_clauses, else_clause):
        self.variable = variable
        self.when_clauses = when_clauses
        if else_clause is None:
            self.else_clause = []
        elif isinstance(else_clause, list):
            self.else_clause = else_clause
        else:
            self.else_clause = [else_clause]

    def __repr__(self):
        return f"CaseStatement(variable={self.variable}, when_clauses={self.when_clauses}, else_clause={self.else_clause})"
